# Encrypted licensed data

`getdeploying_api/<vintage>.tar.gz.enc`: GetDeploying API downloads (D60).
They are encrypted with AES-256-CBC (PBKDF2, 600,000 iterations); the
passphrase is the `GETDEPLOYING_API_KEY` secret. The raw rows are licensed
for research use and are not redistributed. Published results use
aggregates only, with credit to GetDeploying.

To decrypt into `var/` (git-ignored):

```bash
openssl enc -d -aes-256-cbc -pbkdf2 -iter 600000 -pass env:GETDEPLOYING_API_KEY \
  -in data/private/getdeploying_api/<vintage>.tar.gz.enc | tar -xz -C var
```
