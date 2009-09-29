"""
Connexions-specific setup functions for customizing Plone

Author: Brent Hendricks
(C) 2005 Rice University
All Rights Reserved.

"""

import zLOG
from Acquisition import aq_base

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Products.CMFCore.DirectoryView import addDirectoryViews

from Products.CNXPloneSite import product_globals

def installProducts(self, portal):
    """Add any necessary portal tools"""
    portal_setup = getToolByName(portal, 'portal_setup')
    import_context = portal_setup.getImportContextID()
    portal_setup.setImportContext(
            'profile-Products.FeatureArticle:default')
    portal_setup.runAllImportSteps()
    portal_setup.setImportContext(
            'profile-Products.CNXContent:default')
    portal_setup.runAllImportSteps()
    portal_setup.setImportContext(import_context)


def customizeMemberdata(self, portal):
    md = getToolByName(portal, 'portal_memberdata')
    #md._setProperty('comment', '')
    MEMBERDATA_PROPERTIES = (
            ('interests', [], 'lines'),
            ('refer', [], 'lines'),
            ('refertext', '', 'string'),
            ('ok_contact_me', 0, 'boolean'),)

    for prop, default, type in MEMBERDATA_PROPERTIES:
        if not md.hasProperty(prop):
            md._setProperty(prop, default, type)


def customizeActions(self, portal):
    pa_tool=getToolByName(portal,'portal_actions')

    pa_tool.addAction('aboutus', 'About', 'string:$portal_url/aboutus/', '', 'View', 'portal_tabs')
    pa_tool.addAction('help', 'Help', 'string:$portal_url/help/', '', 'View', 'portal_tabs')
    #pa_tool.addAction('qstart', 'Quick Start', 'string:$portal_url/help/qstart/', '', 'View', 'site_actions')
    pa_tool.addAction('contact', 'Contact', 'string:$portal_url/aboutus/contact', '', 'View', 'site_actions')

def customizeSkins(self, portal):
    skinstool = getToolByName(portal, 'portal_skins')


    # We need to add Filesystem Directory Views for any directories
    # in our skins/ directory.  These directories should already be
    # configured.
    addDirectoryViews(skinstool, 'skins', product_globals)
    zLOG.LOG("CNXSitePolicy", zLOG.INFO, "Added 'CNXPloneSite' directory view to portal_skins")
    
    # FIXME: we need a better way of constructing this
    pathlist= [p.strip() for p in skinstool.getSkinPath('Rhaptos').split(',')]
    pathlist.insert(1, 'CNXPloneSite')
    pathlist.insert(1, 'cnx_overrides')
    path = ','.join(pathlist)

    # Create a new 'Connexions' skin
    skinstool.addSkinSelection('Connexions', path, make_default=1)
    zLOG.LOG("CNXSitePolicy", zLOG.INFO, "Added 'Connexions' as new default skin")

def customizeTypes(self, portal):
    types_tool=getToolByName(portal,'portal_types')

    # New 'Paper' type based on file
    types_tool.manage_addTypeInformation(id='Paper',
                                         add_meta_type="Factory-based Type Information",
                                         typeinfo_name="CMFDefault: Portal File")
    paper = getattr(types_tool, 'Paper')
    actions=paper._cloneActions()
    for a in actions:
        if a.id == 'edit':
            a.action = Expression('string:${object_url}/paper_edit_form')
    paper._actions=actions

    # New 'Presentation' type based on file
    types_tool.manage_addTypeInformation(id='Presentation',
                                         add_meta_type="Factory-based Type Information",
                                         typeinfo_name="CMFDefault: Portal File")
    pres = getattr(types_tool, 'Presentation')
    pres.manage_changeProperties(content_icon='ppt_icon.png')
    actions=pres._cloneActions()
    for a in actions:
        if a.id == 'edit':
            a.action = Expression('string:${object_url}/presentation_edit_form')
    pres._actions=actions

    # New 'Blog Item' type based on 'News Item'
    types_tool.manage_addTypeInformation(id='Blog Item',
                                         add_meta_type="Factory-based Type Information",
                                         typeinfo_name="CMFDefault: News Item")
    blog = getattr(types_tool, 'Blog Item')
    actions=blog._cloneActions()
    for a in actions:
        if a.id == 'view':
            a.action = Expression('string:${object_url}/blogitem_view')
    blog._actions=actions

    # New 'Blog Folder' type based on 'Folder'
    types_tool.manage_addTypeInformation(id='Blog Folder',
                                         add_meta_type="Factory-based Type Information",
                                         typeinfo_name="CMFPlone: Plone Folder")
    bf = getattr(types_tool, 'Blog Folder')
    actions=bf._cloneActions()
    for a in actions:
        if a.id == 'folderlisting':
            a.visible = 0
        if a.id == 'view':
            a.action = Expression('string:${folder_url}/blogfolder_view')
        a.category = 'object'
    bf._actions=actions


def customizeForms(self, portal):

    # FIXME: This should be redone using CMFFormController
    props_tool=getToolByName(portal,'portal_properties')

    props_tool.form_properties._setProperty('paper_edit_form', 'validate_id,validate_file_edit')
    props_tool.form_properties._setProperty('presentation_edit_form', 'validate_id,validate_file_edit')        
    props_tool.navigation_properties._setProperty('paper.paper_edit_form.success', 'script:file_edit')
    props_tool.navigation_properties._setProperty('paper.paper_edit_form.failure', 'script:paper_edit_form')
    props_tool.navigation_properties._setProperty('presentation.presentation_edit_form.success', 'script:file_edit')
    props_tool.navigation_properties._setProperty('presentation.presentation_edit_form.failure', 'script:presentation_edit_form')


def customizeFrontPage(self, portal):
    # FIXME: currently disabled until we have better text to go here
    portal.manage_delObjects('index_html')
    portal.invokeFactory('Document', 'frontpage')
    frontpage = portal.frontpage
    frontpage.title = 'Portal Front Page'
    frontpage.edit('html',
                   """<a href="frontpage/document_edit_form">Edit the front page</a>"""
                   )
        
functions = {
    'Install Products': installProducts,
    'Customize Member Data': customizeMemberdata,
    'Customize Actions': customizeActions,
    'Customize Skins': customizeSkins,
    'Customize Types': customizeTypes,
# XXX commented this out because it is broken and doesn't appear to be used
#    'Customize Forms': customizeForms,
    'Customize Front Page': customizeFrontPage,
    }

class CNXSetup:
    type = 'Connexions Setup'

    description = "Site customizations for Connexions"

    functions = functions

    ## This line and below may not be necessary at some point
    ## in the future. A future version of Plone may provide a
    ## superclass for a basic SetupWidget that will safely
    ## obviate the need for these methods.
     
    single = 0
  
    def __init__(self, portal):
        self.portal = portal
  
    def setup(self):
        pass
 
    def delItems(self, fns):
        out = []
        out.append(('Currently there is no way to remove a function', zLOG.INFO))
        return out
 
    def addItems(self, fns):
        out = []
        for fn in fns:
            self.functions[fn](self, self.portal)
            out.append(('Function %s has been applied' % fn, zLOG.INFO))
        return out
 
    def active(self):
        return 1
                                                                                 
    def installed(self):
        return []
 
    def available(self):
        """ Go get the functions """
        # We return an explicit list here instead of just functions.keys() since order matters
        return [
            'Install Products',
            'Customize Member Data',
            'Customize Actions',
            'Customize Skins',
            'Customize Types',
#            'Customize Forms',
            'Customize Front Page',
            ]
