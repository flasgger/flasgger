#!/bin/bash

# Define variables
CHANGELOG_FILE="CHANGELOG_DELTA.md"
TMP_LOG_FILE="tmp.log"
COMMIT_SINCE_HASH="acbf620b31a8a50eade14705908499d8a937f13a"

# Create empty changelog file
touch $CHANGELOG_FILE

# Add header to changelog file
echo "Changelog" >> $CHANGELOG_FILE
echo "=========" >> $CHANGELOG_FILE
echo "" >> $CHANGELOG_FILE

# Generate log file from git history
git log $COMMIT_SINCE_HASH.. --pretty=format:"%s" > $TMP_LOG_FILE

# Loop through log file and add entries to changelog file
while read -r line; do
    echo "- $line" >> $CHANGELOG_FILE
done < $TMP_LOG_FILE

# Remove temporary log file
rm $TMP_LOG_FILE

echo "Changelog file generated: $CHANGELOG_FILE"