#!/usr/bin/env python3.10
"""
binary_cache

Module containing the BinaryCache class.

Author: Marek Križan
Date: 1.5.2024
"""

import os
import cache_server_app.src.config as config
import json
import time
import base64
import ed25519
from cache_server_app.src.database import CacheServerDatabase

class BinaryCache():
    """
    Class to represent binary cache.

    Attributes:
        cache_dir: directory where cache stores NAR files
        database: object to handle database connection
        id: binary cache id
        name: binary cache name
        url: binary cache url
        token: binary cache JWT authentication token
        access: binary cache access ('public'/'private')
        port: port on which binary cache listens
        retention: binary cache retention
    """

    def __init__(self, id: str, name: str, url: str, token: str, access: str, port: int, retention: int):
        self.cache_dir = os.path.join(config.cache_dir, name)
        self.database = CacheServerDatabase()
        self.id = id
        self.name = name
        self.url = url
        self.token = token
        self.access = access
        self.port = port
        self.retention = retention

    @staticmethod
    def get(name: str):
        row = CacheServerDatabase().get_binary_cache_row(name)
        if not row:
            return None
        return BinaryCache(row[0], row[1], row[2], row[3], row[4], int(row[5]), int(row[6]))
    
    @staticmethod
    def get_by_port(port: int):
        row = CacheServerDatabase().get_binary_cache_row_by_port(port)
        if not row:
            return None
        return BinaryCache(row[0], row[1], row[2], row[3], row[4], row[5], row[6])

    def save(self) -> None:
        self.database.insert_binary_cache(self.id, self.name, self.url, self.token, self.access, self.port, self.retention)

    def update(self) -> None:
        self.database.update_binary_cache(self.id, self.name, self.url, self.token, self.access, self.port, self.retention)

    def delete(self) -> None:
        self.database.delete_all_cache_paths(self.name)
        self.database.delete_binary_cache(self.name)

    def cache_json(self, permission: str) -> str:
        with open(os.path.join(self.cache_dir, 'key.pub'), 'r') as f:
            public_key = f.read()

        return json.dumps({
            'githubUsername': '',
            'isPublic': (self.access == 'public'),
            'name': self.name,
            'permission': permission, #TODO
            'preferredCompressionMethod': 'XZ',
            'publicSigningKeys': [public_key],
            'uri': self.url
        })
    
    def cache_workspace_dict(self) -> dict:
        with open(os.path.join(self.cache_dir, 'key.pub'), 'r') as f:
            public_key = f.read()
        
        return {
            'cacheName': self.name,
            'isPublic': (self.access == 'public'),
            'publicKey': public_key.split(':')[1]
        }
    
    def get_store_hashes(self) -> list[str]:
        return [path[1] for path in self.database.get_cache_store_paths(self.name)]
                
    def get_missing_store_hashes(self, hashes: list) -> list:
        return [store_hash for store_hash in hashes if store_hash not in self.get_store_hashes()]
        
    def get_paths(self) -> list:
        return self.database.get_cache_store_paths(self.name)
    
    def update_workspaces(self, new_name: str) -> None:
        self.database.update_cache_in_workspaces(self.name, new_name)

    def update_paths(self, new_name: str) -> None:
        self.database.update_cache_in_paths(self.name, new_name)
    
    def garbage_collector(self):
        while True:
            self.collect_garbage()
            time.sleep(3600)
    
    def collect_garbage(self) -> None:
        for file in os.listdir(self.cache_dir):
            file_age = (os.path.getctime(os.path.join(self.cache_dir, file)) - time.time()) / 604800
            if file_age > self.retention:
                os.remove(file)

    def generate_keys(self) -> None:
        sk, pk = ed25519.create_keypair()

        prefix = "{}.{}-1:".format(self.name, config.server_hostname).encode('utf-8')

        with open(os.path.join(self.cache_dir, 'key.priv'), 'wb') as f:
            f.write(prefix + base64.b64encode(sk.to_bytes()))

        with open(os.path.join(self.cache_dir, 'key.pub'), 'wb') as f:
            f.write(prefix + base64.b64encode(pk.to_bytes()))
