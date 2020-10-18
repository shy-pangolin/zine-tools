#!/usr/local/bin/python3

import argparse
import jinja2
import os

from jinja2 import Template
from pprint import pprint


def round_pages(pages):
    if pages % 4 == 0:
        return pages
    else:
        rounded_pages = (pages + 4) - (pages % 4)
        return rounded_pages


def get_page_pairs(page_ct):
    current_low = 1
    current_high = page_ct
    # NOTE: low_right exists to tell us which side the smaller of the two
    #       numbers belongs on. We set it to true initially because the first
    #       page should always be on the right side of a bifold zine
    low_right = True
    pairs = list()
    while current_low + 1 != current_high:
        if low_right:
            current_pair = ( current_high, current_low )
            low_right = False
        else:
            current_pair = (current_low, current_high)
            low_right = True
        pairs.append(current_pair)
        current_high = current_high - 1
        current_low = current_low + 1 
    current_pair = (current_low, current_high)
    pairs.append(current_pair)
    return pairs
            
def generate_pages(page_pairs, latex_jinja_env):
    content_pages = ''
    for page in page_pairs:
        template = latex_jinja_env.get_template('content_page.tex')
        content_pages += template.render(leftnum=page[0],
                                         rightnum=page[1])
    return content_pages

def write_latex(zine_template, project):
    # TODO: set standard path for this at some point
    project_file = './%s.tex' % project 
    zine_template.stream().dump(project_file)


def main():
    parser = \
        argparse.ArgumentParser(description='Dynamic LaTeX zine template '
                                            'generation tool')
    parser.add_argument('-p', '--pages', required='true', type=int,
                        help='Number of pages needed for content. If not '
                             'divisible by 4, pages will be rounded up')
    parser.add_argument('--project', required='true',
                        help='Name of the zine project you want to generate '
                             'All resulting files will be stashed in your '
                             'local projects directory')
    parser.add_argument('--to-screen', action='store_true', dest='to_screen',
                        help='Output resulting LaTeX to screen instead of to '
                             'a file in the projects directory')
    # Add path and project name options later
    args = parser.parse_args() 
    content_page_ct = round_pages(args.pages)
    page_pairs = get_page_pairs(content_page_ct)
    # pprint(page_pairs)
    # NOTE: We need to customize the way we work with jinja here, since LaTex
    #       and jinja overload certain symbols
    latex_jinja_env = jinja2.Environment(
	block_start_string = '\BLOCK{',
	block_end_string = '}',
	variable_start_string = '\VAR{',
	variable_end_string = '}',
	comment_start_string = '\#{',
	comment_end_string = '}',
	line_statement_prefix = '%%',
	line_comment_prefix = '%#',
	trim_blocks = True,
	autoescape = False,
	loader = jinja2.FileSystemLoader(os.path.abspath('.'))
    )
    content_pages = generate_pages(page_pairs, latex_jinja_env)
    zine_template = latex_jinja_env.get_template('zine_wrapper.tex')
    if args.to_screen:
        print(zine_template.render(content_pages=content_pages))
    else:
        write_latex(zine_template, args.project)

main()
