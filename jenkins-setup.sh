#!/bin/bash

# Jenkins Configuration Setup Script
# This script helps set up Jenkins for the SPE_MP pipeline

set -e

echo "🔧 Jenkins Configuration Helper"
echo "================================"
echo ""

# Check if running with sudo
if [[ $EUID -eq 0 ]]; then
    echo "✓ Running with sudo privileges"
else
    echo "⚠ Some operations may need sudo"
fi

echo ""
echo "📋 Pre-flight Checks"
echo "===================="

# Check docker
if command -v docker &> /dev/null; then
    echo "✓ Docker installed: $(docker --version)"
else
    echo "✗ Docker not found - required for builds"
fi

# Check kubernetes
if command -v kubectl &> /dev/null; then
    echo "✓ kubectl installed: $(kubectl version --short 2>/dev/null || echo 'available')"
else
    echo "⚠ kubectl not found - will be auto-installed by pipeline"
fi

# Check python
if command -v python3 &> /dev/null; then
    echo "✓ Python3 installed: $(python3 --version)"
else
    echo "⚠ Python3 not found - will be auto-installed by pipeline"
fi

# Check git
if command -v git &> /dev/null; then
    echo "✓ Git installed: $(git --version)"
else
    echo "✗ Git not found - required"
fi

echo ""
echo "🐳 Docker Setup"
echo "==============="

if command -v docker &> /dev/null; then
    # Check if jenkins user can access docker
    if groups jenkins | grep -q docker; then
        echo "✓ jenkins user has docker access"
    else
        read -p "Add jenkins user to docker group? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo usermod -aG docker jenkins
            echo "✓ jenkins user added to docker group"
            echo "  Note: Jenkins service needs restart for changes to take effect"
        fi
    fi
    
    # Check docker socket
    if [ -S /var/run/docker.sock ]; then
        echo "✓ Docker socket available at /var/run/docker.sock"
    else
        echo "✗ Docker socket not found"
    fi
else
    echo "⚠ Docker not installed - skipping docker setup"
fi

echo ""
echo "📁 Jenkins Home Directory"
echo "=========================="

JENKINS_HOME="/var/lib/jenkins"
if [ -d "$JENKINS_HOME" ]; then
    echo "✓ Jenkins home: $JENKINS_HOME"
    echo "  Workspace: $JENKINS_HOME/workspace"
else
    echo "⚠ Jenkins home not found at $JENKINS_HOME"
fi

echo ""
echo "🔑 Credentials Setup"
echo "===================="
echo ""
echo "To complete pipeline setup, add these credentials in Jenkins:"
echo ""
echo "1. Docker Hub Credentials"
echo "   - Go to: Manage Jenkins → Manage Credentials → Add Credentials"
echo "   - Kind: Username with password"
echo "   - Scope: Global"
echo "   - Username: <your-dockerhub-username>"
echo "   - Password: <your-dockerhub-token or password>"
echo "   - ID: docker-hub-credentials"
echo ""
echo "2. Kubernetes Config"
echo "   - Go to: Manage Jenkins → Manage Credentials → Add Credentials"
echo "   - Kind: Secret file"
echo "   - Scope: Global"
echo "   - File: Upload your kubeconfig file"
echo "   - ID: kubeconfig"
echo ""

echo ""
echo "🔗 GitHub Webhook Setup"
echo "======================="
echo ""
echo "To auto-trigger builds on git push:"
echo ""
echo "1. Go to: GitHub Repo → Settings → Webhooks → Add webhook"
echo "2. Payload URL: http://<your-jenkins-url>/github-webhook/"
echo "3. Content type: application/json"
echo "4. Events: Just the push event"
echo "5. Add webhook"
echo ""

echo ""
echo "📋 Configuration Files"
echo "====================="
echo ""
echo "Your repository has:"
echo "  ✓ Jenkinsfile - Main pipeline (with DinD support)"
echo "  ✓ Jenkinsfile.simple - Alternative simple version"
echo "  ✓ JENKINS_FIXES.md - Detailed troubleshooting guide"
echo "  ✓ JENKINS_QUICK_FIX.md - Quick reference"
echo ""

echo ""
echo "🚀 Next Steps"
echo "============="
echo ""
echo "1. Review JENKINS_QUICK_FIX.md for summary"
echo "2. Review JENKINS_FIXES.md for detailed fixes"
echo "3. Add credentials in Jenkins (see above)"
echo "4. Push changes to GitHub:"
echo "   git add Jenkinsfile"
echo "   git commit -m 'Fix Jenkins pipeline'"
echo "   git push origin main"
echo "5. Jenkins will auto-trigger (if webhook configured)"
echo "6. Or manually click 'Build Now' in Jenkins"
echo ""

echo ""
echo "📝 Troubleshooting"
echo "=================="
echo ""
echo "If build fails:"
echo "1. Check console output in Jenkins"
echo "2. Read JENKINS_FIXES.md for specific error"
echo "3. Verify credentials are added"
echo "4. Try Jenkinsfile.simple if DinD issues"
echo "5. Check docker socket: ls -la /var/run/docker.sock"
echo ""

echo ""
echo "✅ Setup Guide Complete"
echo ""
echo "For more details, see:"
echo "  - JENKINS_QUICK_FIX.md"
echo "  - JENKINS_FIXES.md"
echo ""
