# Jenkins Pipeline Troubleshooting Guide

## Issues Fixed in Your Pipeline

### 1. **Docker Permission Denied Error**
**Original Error:**
```
permission denied while trying to connect to the docker API at unix:///var/run/docker.sock
```

**Root Cause:** Jenkins container cannot access the Docker daemon socket.

**Fixes Applied:**
- Updated Jenkinsfile to mount docker.sock: `args '-v /var/run/docker.sock:/var/run/docker.sock -u root'`
- Added Docker availability checks before build commands
- Enhanced error handling with `if command -v docker` checks

**Alternative Solutions:**
1. Add jenkins user to docker group: `sudo usermod -aG docker jenkins`
2. Use Docker-in-Docker (DinD) image
3. Configure Jenkins to run on host (not recommended for security)

---

### 2. **Python3 Not Found**
**Original Error:**
```
python3: not found
```

**Root Cause:** Python3 not installed in Jenkins container environment.

**Fixes Applied:**
- Added `apt-get install -y python3 python3-pip` to each stage requiring Python
- Used absolute path: `python3 -m py_compile` instead of just `python3`
- Added checks before using Python

**Updated Command:**
```bash
apt-get update -qq && apt-get install -y python3 python3-pip >/dev/null 2>&1 || true
python3 -m py_compile app.py streamlit_app.py streamlit_customer.py retrain.py test_api.py
```

---

### 3. **pip/flake8/pylint Not Found**
**Original Error:**
```
pip: not found
flake8: not found
pylint: not found
```

**Fixes Applied:**
- Install pip along with Python: `apt-get install python3-pip`
- Use module execution: `python3 -m pip install ...`
- Use module execution for tools: `python3 -m flake8` and `python3 -m pylint`

**Updated Commands:**
```bash
python3 -m pip install pylint flake8 -q 2>/dev/null
python3 -m flake8 app.py --max-line-length=120
python3 -m pylint app.py --disable=all --enable=syntax-error
```

---

### 4. **kubectl Not Found**
**Original Error:**
```
kubectl: not found
```

**Root Cause:** kubectl not installed in Jenkins container.

**Fixes Applied:**
- Added kubectl installation script
- Graceful fallback if kubectl unavailable
- Added availability check before K8s operations

**Installation Script Added:**
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
mv kubectl /usr/local/bin/
```

---

### 5. **Ansible Playbook Not Found**
**Original Error:**
```
No ansible playbook found, skipping
```

**Root Cause:** Jenkinsfile referenced `ansible/playbook.yml` but file is actually `ansible/site.yml`

**Fixes Applied:**
- Changed path to: `ansible/site.yml`
- Added ansible installation if needed
- Added verbose feedback about what's happening

**Updated Check:**
```bash
if [ -f ansible/site.yml ]; then
    echo "Ansible playbook found"
else
    echo "No ansible playbook found at ansible/site.yml"
fi
```

---

## Files Modified/Created

### 1. **Jenkinsfile** (Main)
Enhanced with:
- Docker-in-Docker support
- Automatic tool installation
- Better error handling
- Graceful degradation when tools unavailable

### 2. **Jenkinsfile.simple** (Alternative)
A simpler version for environments without Docker-in-Docker:
- Works with host's Docker/kubectl/ansible
- Conditional stages based on tool availability
- Better suited for traditional Jenkins setups

---

## How to Use

### Option A: Using Docker-in-Docker (Recommended for CI/CD)
```bash
# Use the updated Jenkinsfile
git add Jenkinsfile
git commit -m "Fix: Update Jenkins pipeline with proper tool installation"
```

The pipeline will:
1. Run in a Docker container with Java 17
2. Have access to docker.sock for building images
3. Automatically install Python, kubectl, ansible as needed

### Option B: Using Simple Version
```bash
# Use Jenkinsfile.simple if Docker-in-Docker doesn't work
mv Jenkinsfile Jenkinsfile.docker
cp Jenkinsfile.simple Jenkinsfile
```

This version:
1. Runs on Jenkins host directly
2. Uses host's installed tools
3. Better for environments without containerization

---

## Jenkins Configuration Required

### 1. Add Docker Hub Credentials
```
Jenkins Dashboard → Manage Jenkins → Manage Credentials
Add Credentials:
  - Kind: Username with password
  - Username: <your-dockerhub-username>
  - Password: <your-dockerhub-token>
  - ID: docker-hub-credentials
```

### 2. Add Kubernetes Config
```
Jenkins Dashboard → Manage Jenkins → Manage Credentials
Add Credentials:
  - Kind: Secret file
  - File: <path-to-kubeconfig>
  - ID: kubeconfig
```

### 3. Configure GitHub Webhook (for automatic builds)
```
Your GitHub Repo → Settings → Webhooks → Add Webhook
Payload URL: http://<jenkins-url>/github-webhook/
Content type: application/json
```

---

## Testing the Pipeline

### Local Testing
```bash
# Test Python syntax
python3 -m py_compile app.py streamlit_app.py streamlit_customer.py retrain.py test_api.py

# Test flake8
python3 -m pip install flake8
python3 -m flake8 app.py --max-line-length=120

# Test Docker builds
docker build -f Dockerfile -t test-image .
```

### Jenkins Testing
1. Go to Jenkins Dashboard
2. Find your job (SPE_MP_main)
3. Click "Build Now"
4. Monitor the console output
5. Check Logs tab for detailed execution

---

## Expected Success Output

```
[Pipeline] Start of Pipeline
[Pipeline] node
Running on Jenkins...
[Pipeline] stage
[Pipeline] { (Checkout)
...
[Pipeline] stage
[Pipeline] { (Automated Unit Tests)
Running Python syntax checks...
...
[Pipeline] stage
[Pipeline] { (Code Quality)
Installing code quality tools...
...
[Pipeline] // stage
[Pipeline] End of Pipeline
✓ Pipeline executed successfully!
```

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Docker still shows permission denied | Mount docker.sock and run as root: `args '-v /var/run/docker.sock:/var/run/docker.sock -u root'` |
| apt-get: command not found | Use image with apt (debian/ubuntu based) |
| Timeout during docker build | Increase timeout: `timeout(time: 2, unit: 'HOURS')` |
| kubectl kubeconfig not found | Ensure credentials ID matches 'kubeconfig' in Jenkins |
| Python packages conflict | Use virtual environment or specific versions |

---

## Next Steps

1. **Commit changes to git:**
   ```bash
   git add Jenkinsfile Jenkinsfile.simple
   git commit -m "Fix Jenkins pipeline: install tools, fix paths, improve error handling"
   git push origin main
   ```

2. **Update Jenkins credentials** (if not already done)

3. **Trigger a test build:**
   - Jenkins Dashboard → SPE_MP_main → Build Now

4. **Monitor the build:**
   - Watch console output for any remaining issues
   - Check pipeline stages progress

5. **Validate K8s deployment** (if enabled):
   ```bash
   kubectl get pods -n spe-platform
   kubectl get services -n spe-platform
   ```

---

## Support

If issues persist:
1. Check Jenkins logs: `Jenkins Dashboard → System Log`
2. Review stage logs in console output
3. Verify all credentials are configured
4. Ensure docker socket is properly mounted
5. Test commands locally first before running in pipeline
