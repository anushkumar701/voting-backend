import sys
import os
import json

def app(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=utf-8')]
    start_response(status, headers)
    
    try:
        import pkg_resources
        packages = {dist.project_name: dist.version for dist in pkg_resources.working_set}
    except Exception as e:
        packages = {"error": str(e)}
        
    data = {
        "python_version": sys.version,
        "sys_path": sys.path,
        "cwd": os.getcwd(),
        "env": {k: v for k, v in os.environ.items() if 'KEY' not in k.upper() and 'SECRET' not in k.upper()},
        "packages": packages
    }
    return [json.dumps(data, indent=2).encode('utf-8')]
