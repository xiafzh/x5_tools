#encoding:utf-8

class SBranchItem:
    def __init__(self, title, proj_path, p4_path, svn_path, video_svn_path):
        self.title = title
        self.projpath = proj_path
        self.p4path = p4_path
        self.svnpath = svn_path
        self.video_svn_path = video_svn_path


class SProjectItem:
    def __init__(self, title):
        self.title = title

