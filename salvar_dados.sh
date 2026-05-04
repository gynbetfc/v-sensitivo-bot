#!/bin/bash
cd /workspaces/v-sensitivo-bot
git add vsens_users/
git commit -m "Backup dados $(date)" 2>/dev/null
git push 2>/dev/null
