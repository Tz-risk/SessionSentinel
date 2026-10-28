// Dictionary to track which domain is open in which tab
const tabDomains = {};

// Listen for tab updates to map tab IDs to their current domain
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (tab.url) {
        try {
            const url = new URL(tab.url);
            // Ignore internal browser pages like chrome:// or edge://
            if (!url.protocol.startsWith('http')) return; 
            
            // Extract the base hostname (example: github.com)
            let hostname = url.hostname;
            // Remove 'www.' to ensure domain matching works cleanly
            if (hostname.startsWith('www.')) {
                hostname = hostname.substring(4);
            }
            tabDomains[tabId] = hostname;
        } catch (e) {
            console.error("[SessionSentinel] URL Parsing Error:", e);
        }
    }
});

// Listen for tab closures
chrome.tabs.onRemoved.addListener((tabId, removeInfo) => {
    const domain = tabDomains[tabId];
    
    if (domain) {
        console.log(`[SessionSentinel] Tab closed. Purging session data for: ${domain}`);
        purgeCookiesForDomain(domain);
        // Clean up the dictionary memory
        delete tabDomains[tabId];
    }
});

// Function to find and delete all cookies associated with the closed domain
function purgeCookiesForDomain(domain) {
    chrome.cookies.getAll({ domain: domain }, (cookies) => {
        for (let cookie of cookies) {
            // Construct the exact URL the cookie belongs to (required by the remove API)
            const protocol = cookie.secure ? "https://" : "http://";
            // Strip leading dot from domain if it exists
            const cleanDomain = cookie.domain.startsWith('.') ? cookie.domain.substring(1) : cookie.domain;
            const cookieUrl = protocol + cleanDomain + cookie.path;
            
            // Delete the token
            chrome.cookies.remove({
                url: cookieUrl,
                name: cookie.name
            }, (details) => {
                if (details) {
                    console.log(`[SessionSentinel] Shredded token: ${details.name} for ${cookieUrl}`);
                }
            });
        }
    });
}