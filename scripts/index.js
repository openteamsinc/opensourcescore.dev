const fs = require('fs');
const axios = require('axios');

// Function to strip versioning from package names
function stripVersion(packageLine) {
    // Regular expression to match version constraints
    return packageLine.split(/[<>=~!]/)[0].trim();
}

async function annotatePackage(packageName) {
    try {
        const response = await axios.get(`https://openteams-score.vercel.app/api/package/pypi/${packageName}`);
        if (response.status === 200) {
            console.log(`::notice file=requirements.txt::Package ${packageName} found with status ${response.data.status}`);
        } else {
            console.log(`::error file=requirements.txt::Package ${packageName} not found.`);
        }
    } catch (error) {
        console.log(`::error file=requirements.txt::Error looking up package ${packageName}: ${error.message}`);
    }
}

async function run() {
    const filePath = 'requirements.txt';

    if (!fs.existsSync(filePath)) {
        console.log('::error::requirements.txt not found!');
        return;
    }

    const packages = fs.readFileSync(filePath, 'utf-8').split('\n').filter(pkg => pkg);
    
    for (const packageLine of packages) {
        const packageName = stripVersion(packageLine);  // Strip the version
        await annotatePackage(packageName);
    }
}

run();