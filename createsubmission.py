#! /usr/bin/env python3
import sys
import os
import shutil
import re
from swutil.files import find_files,zip_dir,read_pdf
from pathlib import Path
import argparse
import tempfile
HOME=str(Path.home())
TEXMF=os.path.join(HOME,'texmf')
TEX_PACKAGES=os.path.join(TEXMF,'tex','latex')
TEX_LIBRARIES = os.path.join(TEXMF,'bibtex','bib','base')
AUXILIARY_FILEENDINGS=['log','aux','dvi','lof','lot','bit','idx','glo','bbl','bcf','ilg','toc','ind','out','blg','fdb_latexmk','fls','upa','upb','synctex.gz']
FORBIDDEN_PATTERNS = {'??':'broken references','[\n?\n]':'broken citations'}
def copy_package(package,path):
    package_path = os.path.join(TEX_PACKAGES,package,package+'.sty')
    re_package = re.compile(r'\\(usepackage|RequirePackage)(\[.*?\])?\{(.*?,)*'+package+r'(,.*?)*?\}')
    for file_path in find_files('*.tex',path,match_name=True):
        with open(file_path,'r') as file:
            for line in file.readlines():
                if re_package.search(line):
                    break
            else:
                continue
            shutil.copy(package_path,os.path.dirname(file_path))

def copy_bibfile(bibpath,path):
    re_mainfile = re.compile(r'\\documentclass')
    for file_path in find_files('*.tex',path,match_name=True):
        with open(file_path,'r') as file:
            for line in file.readlines():
                if re_mainfile.search(line):
                    break
            else:
                continue
            shutil.copy(bibpath,os.path.dirname(file_path))

def create_submission(fromm,to,bibliography='library.bib'):
    if fromm[-1] ==os.sep:
        fromm=fromm[:-1]
    zip_path = to+'.zip'
    with tempfile.TemporaryDirectory() as tmpdir:#Now that the desired zip path has been created, the target can be replaced by temporary directory'
        to = os.path.join(tmpdir,'submission')#mkdtemp creates the directory but copytree below also tries to make the directory that is passed to it and fails else'
        if os.path.exists(zip_path):
            print(f'{zip_path} already exists')
            sys.exit(1)
        errors = {}
        for file in find_files('*.pdf',fromm):
            txt = read_pdf(file,split_pages = True)
            matches = {pattern:[i for (i,page) in enumerate(txt) if pattern in page]
                    for pattern in FORBIDDEN_PATTERNS} 
            matches ={pattern:matches[pattern] for pattern in matches if matches[pattern]}
            if matches:
                errors[file] = matches
        if errors:
            [print(f'File {file} seems to contain {FORBIDDEN_PATTERNS[pattern]} on '
            f'page{"s" if len(errors[file][pattern])>1 else ""} {", ".join(str(i+1) for i in errors[file][pattern])}') for file
            in errors for pattern in errors[file]]
            cont = input('Continue? (y/n)')
            if cont not in ['y','Y']:
                sys.exit()
        shutil.copytree(fromm,to)
        delete = [ file for ending in AUXILIARY_FILEENDINGS for file in find_files('*.'+ending,to)]
        for file in delete:
            os.remove(file)
        packages = os.listdir(TEX_PACKAGES)
        for package in packages:
            copy_package(package,to)
        bibfiles = find_files(bibliography,TEX_LIBRARIES,match_name=True)
        for bibfile in bibfiles:
            copy_bibfile(bibfile,to)
        zip_dir(zip_path,to,rename_source_dir = os.path.basename(fromm))
        print(f'Successfully created {zip_path}')

if __name__=='__main__':
    class LineWrapRawTextHelpFormatter(argparse.RawDescriptionHelpFormatter):
        def _split_lines(self, text, width):
            text = self._whitespace_matcher.sub(' ', text).strip()
            return _textwrap.wrap(text, width)
    parser=argparse.ArgumentParser(formatter_class=LineWrapRawTextHelpFormatter)
    parser.add_argument('source',action='store')
    parser.add_argument('target',action='store')
    args=parser.parse_args()
    create_submission(args.source,args.target)
