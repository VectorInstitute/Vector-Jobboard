import base64
import configparser

from github import Github, InputGitTreeElement


def push_to_github(fnames: list[str], message: str = "") -> None:
    # user = "GithubUsername"
    # password = "*********"
    # g = Github(user,password)
    config = configparser.ConfigParser()
    config.read('config.ini')
    access_token = config['GITHUB']['access_token']
    g = Github(access_token)
    repo = g.get_user().get_repo('Vector-Jobboard') # repo name
    
    master_ref = repo.get_git_ref('heads/gh-pages')
    master_sha = master_ref.object.sha
    base_tree = repo.get_git_tree(master_sha)

    element_list = list()
    for i, entry in enumerate(fnames):
        with open(entry, encoding="utf8") as input_file:
            data = input_file.read()
        if entry.endswith('.png'): # images must be encoded
            data = base64.b64encode(data)
        element = InputGitTreeElement(fnames[i], '100644', 'blob', data)
        element_list.append(element)

    tree = repo.create_git_tree(element_list, base_tree)
    parent = repo.get_git_commit(master_sha)
    commit = repo.create_git_commit(message, tree, [parent])
    master_ref.edit(commit.sha)

if __name__ == "__main__":
    push_to_github(['profiles.csv'])