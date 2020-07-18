import requests
import argparse
import datetime
import logging
import re

service_template = """# {service_name}
Version: {version}

{toc}

{resources}

{copyright}
"""

resource_markdown_template = """
## {title}

* __path:__ {path}
* __methods:__ {methods}
* __type:__ {type}

{details}

### Params
| Param   | type | default | required | details | spec | many | label |
|---------|------|---------|----------|---------|------|------|-------|
{params}

### Fields
| Field   | type | write_only | read_only | details | spec | label |
|---------|------|------------|-----------|---------|------|-------|
{fields}

"""

param_row = "| {param} | {type} | {default} |  {required} |  {details} |  {spec} |  {many} |  {label} |"

field_row = "| {field} | {type} | {write_only} |  {read_only} |  {details} |  {spec} | {label} |"


def to_markdown(document):
    """

    Args:
        document:

    Returns:

    """
    return resource_markdown_template.format(**document)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--baseurl", help="base url to hit with OPTIONS requests")
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    parser.add_argument("-s", "--single-page", help="aggregate all resources in a single markdown page",
                        action="store_true")
    parser.add_argument("-toc", "--table-of-contents", help="create auto table of contents",
                        action="store_true")
    parser.add_argument("-dv", "--doc-version", help="document version, default is 0.0.1")
    parser.add_argument("-sn", "--service-name", help="service name")
    parser.add_argument("-o", "--output-file", help="service name")
    args = parser.parse_args()

    version = args.doc_version if args.doc_version else '0.0.1'
    out_file = args.output_file if args.output_file else 'output.md'

    if not args.service_name:
        raise Exception("You have to specify Service Name")

    if not args.baseurl:
        raise ValueError("Baseurl can not be blank")

    if args.table_of_contents:
        toc = ["## Table of Contents"]

    r = requests.get(args.baseurl)
    r = r.json()
    endpoints = r.get('content')

    rendered_resources = {}
    for e in endpoints:
        try:
            response = requests.options("%s%s" % (args.baseurl, e["url"]))
            docstring = response.json()

            params = []
            if docstring['params']:
                for k, v in docstring['params'].items():
                    v['param'] = k
                    params.append(param_row.format(**v))
                docstring['params'] = "\n".join(params)

            fields = []
            if docstring['fields']:
                for k, v in docstring['fields'].items():
                    v['field'] = k
                    fields.append(field_row.format(**v))
                docstring['fields'] = "\n".join(fields)

            details = docstring['details']

            rendered_resources.update({docstring['name']: to_markdown(docstring)})

            if args.table_of_contents:
                toc.append("* [{title}](#{lower_name})".format(
                                                        title=docstring['title'],
                                                        lower_name=re.sub('[^a-zA-Z0-9-]', '', docstring['title'].lower().replace(" ", "-"))
                ))

        except Exception as e:
            logging.error("Error: {}".format(e))

    if args.single_page:
        final_doc = service_template.format(
            toc="\n\n".join(toc),
            resources="\n\n".join(rendered_resources.values()),
            service_name=args.service_name,
            version=version,
            copyright="All rights reserved zops.io, generated at {:%d %b %Y %H:%M}".format(datetime.datetime.now())
        )

        with open('dist/%s' % out_file, 'w') as f:
            f.write(final_doc)
    else:
        for name, content in rendered_resources:
            final_doc = service_template.format(
                resources=content,
                service_name=args.service_name,
                version=version,
                copyright="All rights reserved zops.io, generated at {:%d %b %Y %H:%M}".format(datetime.datetime.now())
            )

            with open('dist/%s.md' % name, 'w') as f:
                f.write(final_doc)
