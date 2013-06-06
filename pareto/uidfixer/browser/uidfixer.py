import re
import urllib
from urlparse import urlparse

from Products.ATContentTypes.content import base

from plone.portlets.interfaces import (
    IPortletManager, IPortletAssignmentMapping, IPortletRetriever,
    ILocalPortletAssignable)
from zope.component import getUtility, getMultiAdapter, ComponentLookupError

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.redirector.interfaces import IRedirectionStorage

# XXX meh, no clue what lib has this anymore... replace once remembered!
def entitize(s):
    s = s.replace('&', '&amp;')
    s = s.replace('"', '&quot;')
    s = s.replace('<', '&lt;')
    s = s.replace('>', '&gt;')
    return s


class UIDFixerView(BrowserView):
    template = ViewPageTemplateFile('uidfixer.pt')
    results_template = ViewPageTemplateFile('uidfixer-results.pt')

    def __call__(self):
        if not self.request.get('submit'):
            return self.template()
        return self.results_template()

    def results(self):
        """ return a nicely formatted list of objects for a template """
        portal_catalog = self.context.portal_catalog
        return [{
            'object': context,
            'field': field,
            'href': href,
            'resolved': not not uid,
            'resolved_url':
                (portal_catalog(UID=uid) and
                    portal_catalog(UID=uid).getObject().absolute_url()),
        } for context, field, href, uid in self.fix(self.context)]

    def fix(self, context, processed_portlets=None):
        if not context.getId().startswith('portal_'):
            if processed_portlets is None:
                processed_portlets = []
            if isinstance(context, base.ATCTContent):
                for info in self.process_content(context):
                    yield info
            # process portlets, both Plone ones and those from Collage
            for info in self.process_portlets(context, processed_portlets):
                yield info
            for item in context.objectValues():
                for info in self.fix(item, processed_portlets):
                    yield info

    def process_portlets(self, context, processed_portlets):
        for manager_name in (
                'plone.leftcolumn', 'plone.rightcolumn',
                'collage.portletmanager'):
            try:
                manager = getUtility(IPortletManager, manager_name, context)
            except ComponentLookupError:
                continue
            if manager:
                retriever = getMultiAdapter(
                    (context, manager), IPortletRetriever)
                for portlet in retriever.getPortlets():
                    assignment = portlet['assignment']
                    if assignment in processed_portlets:
                        continue
                    processed_portlets.append(assignment)
                    if hasattr(assignment, 'text'):
                        html = assignment.text
                        fixed = False
                        for href, uid in self.find_uids(html, context):
                            if uid:
                                html = html.replace(
                                    'href="%s' % (href,),
                                    'href="resolveuid/%s' % (uid,))
                                fixed = True
                            yield (
                                context, portlet,
                                href, uid)
                        if fixed and not self.request.get('dry'):
                            assignment.text = html
                            assignment._p_changed = True

    def process_content(self, context):
        fields = context.schema.fields()
        for field in fields:
            if (field.type != 'text' or
                    field.default_output_type != 'text/x-html-safe'):
                continue
            fieldname = field.getName()
            html = field.getRaw(context)
            fixed = False
            for href, uid in self.find_uids(html, context):
                if not uid:
                    # html = html.replace(href, 'UNRESOLVED:/%s' % (uid,))
                    pass
                else:
                    html = html.replace(
                        'href="%s' % (href,),
                        'href="resolveuid/%s' % (uid,))
                fixed = True
                yield context, field, href, uid
            if fixed and not self.request.get('dry'):
                field.set(context, html)

    def convert_link(self, href, context):
        if '/resolveuid/' in href:
            _, uid = href.split('/resolveuid/')
            return uid
        elif '/resolveUid/' in href and self.request.get('fck'):
            _, uid = href.split('/resolveUid/')
            return uid
        else:
            try:
                context = self.resolve_redirector(href, context)
            except (KeyError, AttributeError):
                pass
            else:
                return context.UID()

    def resolve_redirector(self, href, context):
        redirector = getUtility(IRedirectionStorage)
        if href.endswith('/'):
            href = href[:-1]
        chunks = [urllib.unquote(chunk) for chunk in href.split('/')]
        while chunks:
            chunk = chunks[0]
            if chunk in ('', '.'):
                chunks.pop(0)
                continue
            elif chunk == '..':
                chunks.pop(0)
                context = context.aq_parent
            else:
                break
        path = list(context.getPhysicalPath()) + chunks
        redirect = redirector.get('/'.join(path))
        if redirect is not None:
            redirected = context.restrictedTraverse(
                redirect.split('/'))
            if redirected is not None:
                context = redirected
            else:
                while chunks:
                    chunk = chunks.pop(0)
                    context = getattr(context, chunk)
        else:
            while chunks:
                chunk = chunks.pop(0)
                context = getattr(context, chunk)
        return context

    _reg_href = re.compile(r'href="([^"]+)"')
    def find_uids(self, html, context):
        while True:
            match = self._reg_href.search(html)
            if not match:
                break
            href = match.group(1)
            # leave any views, GET vars and hashes alone
            # not entirely correct, but this seems
            # relatively solid
            for s in ('@@', '?', '#', '++'):
                if s in href:
                    href = href[:href.find(s)]
            html = html.replace(match.group(0), '')
            scheme, netloc, path, params, query, fragment = urlparse(href)
            if not scheme and not href.lower().startswith('resolveuid/'):
                # relative link, convert to resolveuid one
                uid = self.convert_link(href, context)
                yield href, uid
