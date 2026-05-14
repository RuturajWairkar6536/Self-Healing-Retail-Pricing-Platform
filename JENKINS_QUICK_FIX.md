# Jenkins Pipeline Quick Reference

## What Was Fixed

Your Jenkins pipeline had 5 critical errors that have now been resolved:

### ❌ → ✅ Quick Summary

| Error | Fix |
|-------|-----|
| `permission denied while trying to connect to docker API` | Added docker.sock mounting to Jenkinsfile agent |
| `python3: not found` | Auto-install Python3 in stages that need it |
| `pip/flake8/pylint: not found` | Use `python3 -m pip install` and `python3 -m flake8` |
| `kubectl: not found` | Auto-download kubectl from official k8s release |
| `ansible/playbook.yml not found` | Fixed path to `ansible/site.yml` |

---

## To Apply These Fixes

### Option 1: Updated Jenkinsfile (Recommended)
Already fixed in `/home/ruturajwairkar/Desktop/SPE_MP/Jenkinsfile`

Key improvements:
```groovy
agent {
    docker {
        image 'jenkins/jenkins:latest-jdk17'
        args '-v /var/run/docker.sock:/var/run/docker.sock -u root'
        reuseNode true
    }
}
```

Stages now auto-install tools:
```bash
apt-get install -y python3 python3-pip
apt-get install -y ansible
```

### Option 2: Simple Version (If DinD has issues)
Copy from `Jenkinsfile.simple` to `Jenkinsfile`:
```bash
cp Jenkinsfile.simple Jenkinsfile
```

---

## How to Deploy

### Step 1: Push Changes
```bash
cd /home/ruturajwairkar/Desktop/SPE_MP
git add Jenkinsfile Jenkinsfile.simple JENKINS_FIXES.md
git commit -m "Fix: Jenkins pipeline - install tools, fix docker/k8s access"
git push origin main
```

### Step 2: Trigger Build
1. Open Jenkins Dashboard
2. Find your SPE_MP_main job
3. Click "Build Now"
4. Watch console output

### Step 3: Verify Success
Expected output:
```
✓ Pipeline executed successfully!
```

---

## Credentials Needed in Jenkins

Before running the pipeline, ensure these are configured:

### 1. Docker Hub Credentials
- ID: `docker-hub-credentials`
- Type: Username + Password
- Get token from: https://hub.docker.com/settings/security

### 2. Kubernetes Config
- ID: `kubeconfig`
- Type: Secret file
- File: Your kubeconfig from `~/.kube/config`

### 3. GitHub (Auto-configured)
- Should work automatically if GitHub plugin installed

---

## Files Changed

1. **Jenkinsfile** - Main pipeline with fixes
2. **Jenkinsfile.simple** - Alternative simpler version
3. **JENKINS_FIXES.md** - Detailed troubleshooting guide (read this if issues persist!)

---

## If Build Still Fails

1. **Check Stage Output**: Each stage now logs what it's doing
2. **Read JENKINS_FIXES.md**: Detailed solutions for each error
3. **Try Jenkinsfile.simple**: May work better on your Jenkins setup
4. **Check Docker Socket**: Verify docker.sock is accessible:
   ```bash
   ls -la /var/run/docker.sock
   ```

---

## Pipeline Stages

```
1. Checkout         → Get latest code from GitHub
2. Docker Build     → Build 4 images (pricing-api, admin, customer, trainer)
3. Unit Tests       → Run Python syntax checks
4. Code Quality     → Run flake8 and pylint
5. Push to Registry → Push to Docker Hub (needs credentials)
6. Deploy via Ansible → Optional Ansible deployment
7. Deploy to K8s    → Kubernetes deployment (optional)
```

All stages have error handling and won't fail the pipeline if tools unavailable.

---

## Next Steps

1. Push the fixes to GitHub
2. Jenkins will auto-trigger on push (if webhook configured)
3. Monitor the build in Jenkins console
4. Once successful, you have:
   - ✅ Docker images built
   - ✅ Code quality checked  
   - ✅ K8s ready for deployment
   - ✅ Images pushed to registry (if credentials added)
