import os
import sys
import datetime
import time
import gobject
import gtk
import appindicator
from github2.client import Github

github = Github('sandboxws', 'API_KEY')

def add_separator(menu):
  separator = gtk.SeparatorMenuItem()
  separator.show()
  menu.append(separator)

# common methods ########################################

# Personal related methods ##############################
def get_personal_repos():
  repos = github.repos.list()
  return repos

def build_personal_repos(menu):
  repos = get_personal_repos()
  menu_item = gtk.MenuItem('Personal')
  menu_item.set_sensitive(False)
  menu_item.show()
  menu.append(menu_item)
  for repo in repos:
    item = gtk.MenuItem(repo.name)
    menu.append(item)
    item.show()

def build_repos(menu):
  repos = github.organizations.repositories()
  section_name = None
  for repo in repos:
    if(section_name == None or section_name != repo.organization):
      add_separator(menu)
      section_name = repo.organization
      menu_item = gtk.MenuItem(section_name)
      menu_item.set_sensitive(False)
      menu_item.show()
      menu.append(menu_item)
    
    item = gtk.MenuItem(repo.name)
    path = repo.organization + "/" + repo.name
    item.connect('activate', build_commits, path)
    add_dummy_menu(item)
    #build_commits(item, path)
    menu.append(item)
    item.show()

def handle_item(item, item_type, commit):
  if(item_type == 'browser'):
    os.system("%s http://github.com%s" % ("sensible-browser", commit.url))

def add_dummy_menu(menu_item):
  submenu = gtk.Menu()
  item = gtk.MenuItem('loading...')
  submenu.append(item)
  menu_item.set_submenu(submenu)
  item.show()

def build_commits(menu_item, path):
  i = 0
  commits = github.commits.list(path)
  if(len(commits) >= 1):
    submenu = gtk.Menu()
    for commit in commits:
      if(i >= 5):
        break
      i += 1
      sha_menu_item = gtk.MenuItem(commit.id)
      sha_menu_item.set_sensitive(False)
      item = gtk.MenuItem(commit.message)
      item.connect('activate', handle_item, 'browser', commit)
      #print len(github.commits.show(path, commit.id).modified)
      submenu.append(sha_menu_item)
      submenu.append(item)
      menu_item.set_submenu(submenu)
      sha_menu_item.show()
      item.show()
      add_separator(submenu)

# Indicator related methods ###########################
def add_quit_menuitem(menu):
  add_separator(menu)
  exit_item = gtk.MenuItem('Quit')
  exit_item.connect('activate', quit_indicator)
  menu.append(exit_item)
  exit_item.show()

def quit_indicator(item):
  sys.exit(0)
  
if __name__ == "__main__":
    ind = appindicator.Indicator("github", "gnome-netstatus-tx",
                                 appindicator.CATEGORY_APPLICATION_STATUS)
    ind.set_label("Github")
    ind.set_status(appindicator.STATUS_ACTIVE)
    
    menu = gtk.Menu()
    build_personal_repos(menu)
    build_repos(menu)
    add_quit_menuitem(menu)

    ind.set_menu(menu)
    gtk.main()
