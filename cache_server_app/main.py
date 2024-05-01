#!/usr/bin/env python3.10
"""
main

The cache-server main module.

Author: Marek Križan
Date: 1.5.2024
"""

import sys
from cache_server_app.src.argument_parsing import handle_arguments

def main():
    handle_arguments(sys.argv[1:])

if __name__ == '__main__':
    main()
