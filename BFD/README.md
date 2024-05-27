BFD is meant to be set up on a separate machine within a Tor relay. The bfd_server.py runs a test server which records tokens
in the directory named token_directory. Current version does not verify tokens as uuid4 and is only used for testing.

**bfd_server.py**: python file to run the BFD server
**token_directory** : the BFD which stores uuid4 tokens
**keys** : keys directory stores hashes for each token
