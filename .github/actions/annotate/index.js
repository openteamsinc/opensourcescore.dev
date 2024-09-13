const fs = require('fs');
const https = require('https');

// Function to strip versioning from package names
function stripVersion(packageLine) {
    return packageLine.split(/[<>=~!]/)[0].trim();
}

// Function to make an API request using the built-in https module
function makeApiRequest(packageName) {
    const url = `https://openteams-score.vercel.app/api/package/pypi/${packageName}`;

    return new Promise((resolve, reject) => {
        https.get(url, (res) => {
            let data = '';

            // Collect the data as it comes in
            res.on('data', (chunk) => {
                data += chunk;
            });

            // End of the response
            res.on('end', () => {
                if (res.statusCode === 200) {
                    resolve(JSON.parse(data));
                } else {
                    reject(`Request failed with status code ${res.statusCode}`);
                }
            });
        }).on('error', (e) => {
            reject(`Error: ${e.message}`);
        });
    });
}

async function annotatePackage(packageName) {
    try {
        const response = await makeApiRequest(packageName);
        if (response && response.source) {
            const { maturity, health_risk } = response.source;
            const maturityValue = maturity ? maturity.value : 'Unknown';
            const healthRiskValue = health_risk ? health_risk.value : 'Unknown';
            
            console.log(`::notice file=requirements.txt::Package ${packageName} found. (Maturity: ${maturityValue}, Health: ${healthRiskValue})`);
        } else {
            console.log(`::error file=requirements.txt::Package ${packageName} not found.`);
        }
    } catch (error) {
        console.log(`::error file=requirements.txt::Error looking up package ${packageName}: ${error}`);
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
