import os
import json
import joblib
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="E-Commerce Return Risk Engine",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Streamlit CSS to remove default margins and fill viewport
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding: 0rem !important;
        max-width: 100% !important;
    }
    .stApp {
        background-color: #fbf9f4;
    }
    </style>
""", unsafe_allow_html=True)

# Google Stitch HTML + JS Template
STITCH_HTML = """
<!DOCTYPE html>
<html class="light" lang="en">
<head>
    <meta charset="utf-8"/>
    <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
    <title>E-Commerce Product Return Risk Engine</title>
    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
    <link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400..900;1,6..96,400..900&family=Hanken+Grotesk:ital,wght@0,100..900;1,100..900&family=JetBrains+Mono:ital,wght@0,100..800;1,100..800&display=swap" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
    <script id="tailwind-config">
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    "colors": {
                        "on-tertiary": "#ffffff",
                        "on-background": "#1b1c19",
                        "on-secondary-container": "#2c6e72",
                        "on-primary-container": "#9eaaff",
                        "on-primary-fixed-variant": "#323f90",
                        "tertiary-fixed-dim": "#ffb787",
                        "on-surface-variant": "#454651",
                        "on-tertiary-fixed-variant": "#723603",
                        "surface-container-lowest": "#ffffff",
                        "secondary": "#25676b",
                        "surface-container-high": "#eae8e3",
                        "on-secondary-fixed-variant": "#004f53",
                        "secondary-fixed-dim": "#92d1d5",
                        "surface-container-low": "#f5f3ee",
                        "primary-fixed": "#dfe0ff",
                        "on-primary-fixed": "#000e5e",
                        "surface-container": "#f0eee9",
                        "tertiary-fixed": "#ffdcc7",
                        "surface-tint": "#4b57a9",
                        "surface-variant": "#e4e2dd",
                        "tertiary": "#4b2100",
                        "on-error": "#ffffff",
                        "background": "#fbf9f4",
                        "inverse-primary": "#bbc3ff",
                        "surface-container-highest": "#e4e2dd",
                        "error": "#ba1a1a",
                        "outline": "#767682",
                        "primary": "#142275",
                        "on-secondary-fixed": "#002022",
                        "primary-container": "#2e3b8c",
                        "primary-fixed-dim": "#bbc3ff",
                        "on-secondary": "#ffffff",
                        "inverse-on-surface": "#f2f1ec",
                        "secondary-fixed": "#aeeef2",
                        "on-primary": "#ffffff",
                        "outline-variant": "#c6c5d3",
                        "surface-bright": "#fbf9f4",
                        "secondary-container": "#aeeef2",
                        "surface-dim": "#dbdad5",
                        "on-surface": "#1b1c19",
                        "on-tertiary-container": "#f09c63",
                        "on-tertiary-fixed": "#311300",
                        "on-error-container": "#93000a",
                        "surface": "#fbf9f4",
                        "inverse-surface": "#30312e",
                        "error-container": "#ffdad6",
                        "tertiary-container": "#6d3300"
                    },
                    "fontFamily": {
                        "body-lg": ["Hanken Grotesk"],
                        "label-caps": ["Hanken Grotesk"],
                        "headline-md": ["Bodoni Moda"],
                        "headline-lg": ["Bodoni Moda"],
                        "body-md": ["Hanken Grotesk"],
                        "data-ui": ["JetBrains Mono"],
                        "display-lg": ["Bodoni Moda"]
                    }
                }
            }
        }
    </script>
    <style>
        body { font-family: 'Hanken Grotesk', sans-serif; background-color: #fbf9f4; color: #1b1c19; }
        .font-headline { font-family: 'Bodoni Moda', serif; }
        .font-data { font-family: 'JetBrains Mono', monospace; }
        .editorial-border { border-color: rgba(18, 18, 18, 0.1); border-width: 1px; }
        .editorial-hairline { border-bottom: 1px solid rgba(18, 18, 18, 0.1); }
        .input-line { border: none; border-bottom: 1px solid #142275; background: transparent; border-radius: 0; padding: 4px 0; }
        .input-line:focus { outline: none; border-bottom-width: 2px; }
        .toggle-checkbox:checked { right: 0; border-color: #142275; }
        .toggle-checkbox:checked + .toggle-label { background-color: #142275; }
        .toggle-checkbox:checked + .toggle-label:after { transform: translateX(100%); border-color: white; }
    </style>
</head>
<body class="antialiased min-h-screen flex">

<!-- SideNavBar -->
<nav class="bg-surface-container-low h-screen w-64 border-r border-outline-variant/30 fixed left-0 top-0 flex flex-col py-6 z-40 hidden md:flex">
    <div class="px-6 mb-8">
        <h1 class="font-headline text-2xl font-medium text-primary tracking-tight">Return Risk Engine</h1>
        <p class="text-xs text-on-surface-variant mt-2 uppercase tracking-widest opacity-70">Editorial Control</p>
    </div>
    <ul class="flex flex-col space-y-1 mt-4 flex-grow">
        <li>
            <a class="flex items-center px-6 py-3 text-primary font-bold border-r-2 border-primary bg-surface-container transition-colors cursor-pointer" href="#">
                <span class="material-symbols-outlined mr-4" style="font-variation-settings: 'FILL' 1;">dashboard</span>
                <span class="text-sm">Overview</span>
            </a>
        </li>
        <li>
            <a class="flex items-center px-6 py-3 text-on-surface-variant/70 hover:bg-surface-container transition-colors cursor-pointer" href="#">
                <span class="material-symbols-outlined mr-4">analytics</span>
                <span class="text-sm">Risk Analysis</span>
            </a>
        </li>
        <li>
            <a class="flex items-center px-6 py-3 text-on-surface-variant/70 hover:bg-surface-container transition-colors cursor-pointer" href="#">
                <span class="material-symbols-outlined mr-4">query_stats</span>
                <span class="text-sm">Metrics</span>
            </a>
        </li>
        <li>
            <a class="flex items-center px-6 py-3 text-on-surface-variant/70 hover:bg-surface-container transition-colors cursor-pointer" href="#">
                <span class="material-symbols-outlined mr-4">history</span>
                <span class="text-sm">History</span>
            </a>
        </li>
        <li class="mt-auto">
            <a class="flex items-center px-6 py-3 text-on-surface-variant/70 hover:bg-surface-container transition-colors cursor-pointer border-t border-outline-variant/10" href="#">
                <span class="material-symbols-outlined mr-4">settings</span>
                <span class="text-sm">Settings</span>
            </a>
        </li>
    </ul>
    <div class="px-6 mt-6">
        <button onclick="evaluateRisk()" class="w-full bg-primary text-on-primary text-xs py-3 uppercase tracking-wider hover:bg-primary-container transition-colors font-bold">Run New Analysis</button>
    </div>
</nav>

<!-- Main Content Area -->
<main class="flex-1 md:ml-64 bg-background min-h-screen">
    <header class="w-full h-16 border-b border-outline-variant/20 flex items-center justify-between px-8 sticky top-0 z-30 bg-background/90 backdrop-blur-sm">
        <div class="hidden md:block">
            <span class="font-data text-xs text-on-surface-variant/60">Engine / Risk Assessment / Active</span>
        </div>
        <div class="flex items-center space-x-6 text-on-surface-variant">
            <button class="hover:text-primary transition-colors">
                <span class="material-symbols-outlined">notifications</span>
            </button>
            <button class="hover:text-primary transition-colors">
                <span class="material-symbols-outlined">account_circle</span>
            </button>
        </div>
    </header>

    <div class="p-8 max-w-7xl mx-auto">
        <div class="mb-8 border-b border-outline-variant/20 pb-8">
            <h2 class="font-headline text-4xl text-on-background mb-4 tracking-tight">Return Risk Engine</h2>
            <p class="text-lg text-on-surface-variant max-w-3xl">
                Real-time ML risk scoring and automated business triggers to optimize post-purchase efficiency.
            </p>
        </div>

        <!-- Main Layout Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <!-- Left Panel: Inputs -->
            <div class="lg:col-span-4 bg-surface-container-lowest p-6 border-r editorial-border shadow-[0_32px_64px_-12px_rgba(20,34,117,0.04)]">
                <h3 class="font-headline text-2xl mb-8 editorial-hairline pb-2">Input Parameters</h3>
                <form id="risk-form" onsubmit="event.preventDefault(); evaluateRisk();" class="space-y-6">
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-bold text-on-surface-variant mb-1 uppercase tracking-wider">Category</label>
                            <select id="product_category" class="w-full input-line font-data text-sm text-on-background">
                                <option value="Clothing" selected>Clothing</option>
                                <option value="Electronics">Electronics</option>
                                <option value="Beauty">Beauty</option>
                                <option value="Home">Home</option>
                                <option value="Books">Books</option>
                                <option value="Toys">Toys</option>
                                <option value="Sports">Sports</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-on-surface-variant mb-1 uppercase tracking-wider">Shipping</label>
                            <select id="shipping_type" class="w-full input-line font-data text-sm text-on-background">
                                <option value="Standard" selected>Standard</option>
                                <option value="Two-Day">Two-Day</option>
                                <option value="Express">Express</option>
                                <option value="Same-Day">Same-Day</option>
                                <option value="Expedited">Expedited</option>
                            </select>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-bold text-on-surface-variant mb-1 uppercase tracking-wider">Price</label>
                            <div class="relative">
                                <span class="absolute left-0 bottom-1 font-data text-sm text-on-surface-variant/50">$</span>
                                <input id="price" class="w-full input-line pl-4 font-data text-sm text-on-background" type="number" step="0.01" value="49.99"/>
                            </div>
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-on-surface-variant mb-1 uppercase tracking-wider">Qty</label>
                            <input id="quantity" class="w-full input-line font-data text-sm text-on-background" type="number" value="1" min="1"/>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-bold text-on-surface-variant mb-1 uppercase tracking-wider">Discount (%)</label>
                            <input id="discount_pct" class="w-full input-line font-data text-sm text-on-background" type="number" value="10" min="0" max="100"/>
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-on-surface-variant mb-1 uppercase tracking-wider">Seller Rating</label>
                            <input id="seller_rating" class="w-full input-line font-data text-sm text-on-background" type="number" step="0.1" value="4.2" min="1.0" max="5.0"/>
                        </div>
                    </div>

                    <div class="editorial-hairline pb-4 pt-4">
                        <h4 class="text-xs font-bold text-on-surface-variant mb-4 uppercase tracking-wider">Customer Profile</h4>
                        <div class="space-y-4">
                            <div class="flex justify-between items-center border-b border-outline-variant/10 pb-2">
                                <span class="text-sm text-on-background">Previous Returns</span>
                                <input id="previous_returns_count" type="number" min="0" max="20" value="2" class="w-16 text-right input-line font-data text-sm text-on-background"/>
                            </div>
                            <div class="flex justify-between items-center border-b border-outline-variant/10 pb-2">
                                <span class="text-sm text-on-background">Account Tenure (Days)</span>
                                <input id="customer_tenure_days" type="number" min="0" value="120" class="w-20 text-right input-line font-data text-sm text-on-background"/>
                            </div>
                            <div class="flex items-center justify-between pt-2">
                                <span class="text-sm text-on-background">Prime Member</span>
                                <input id="is_prime_member" type="checkbox" checked class="w-5 h-5 accent-primary cursor-pointer"/>
                            </div>
                        </div>
                    </div>

                    <button type="submit" class="w-full bg-primary text-on-primary text-xs font-bold py-4 uppercase tracking-widest mt-8 hover:bg-primary-container transition-colors shadow-md">
                        Evaluate Return Risk
                    </button>
                </form>
            </div>

            <!-- Right Panel: Results -->
            <div class="lg:col-span-8 flex flex-col space-y-8 pl-0 lg:pl-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <!-- Score Card -->
                    <div class="p-8 editorial-border relative overflow-hidden bg-white">
                        <div id="risk_bg_accent" class="absolute top-0 right-0 w-32 h-32 bg-error/5 rounded-bl-full -mr-16 -mt-16"></div>
                        <h4 class="text-xs font-bold text-on-surface-variant mb-6 uppercase tracking-widest">Risk Score</h4>
                        <div class="flex items-baseline mb-2">
                            <span id="risk_score_val" class="font-headline text-6xl font-semibold text-error">77</span>
                            <span class="font-headline text-2xl text-on-surface-variant/50 ml-2">/100</span>
                        </div>
                        <div class="mt-4 flex items-center">
                            <span id="risk_tier_badge" class="inline-block px-3 py-1 text-xs font-bold uppercase tracking-wider border border-error text-error bg-error/5">High Risk</span>
                        </div>
                    </div>

                    <!-- Probability Meter -->
                    <div class="p-8 editorial-border bg-surface-container-low">
                        <h4 class="text-xs font-bold text-on-surface-variant mb-6 uppercase tracking-widest">Return Probability</h4>
                        <div id="return_prob_val" class="text-4xl font-data text-on-background mb-4">77.3%</div>
                        
                        <!-- Segmented Bar -->
                        <div id="segmented_bar" class="flex h-2 w-full gap-1 mt-8">
                            <div class="h-full flex-1 bg-primary transition-all duration-300"></div>
                            <div class="h-full flex-1 bg-primary transition-all duration-300"></div>
                            <div class="h-full flex-1 bg-primary transition-all duration-300"></div>
                            <div class="h-full flex-1 bg-primary transition-all duration-300"></div>
                            <div class="h-full flex-1 bg-primary transition-all duration-300"></div>
                            <div class="h-full flex-1 bg-error transition-all duration-300"></div>
                            <div class="h-full flex-1 bg-error transition-all duration-300"></div>
                            <div class="h-full flex-1 bg-error transition-all duration-300"></div>
                            <div class="h-full flex-1 bg-outline-variant/30 transition-all duration-300"></div>
                            <div class="h-full flex-1 bg-outline-variant/30 transition-all duration-300"></div>
                        </div>
                        <div class="flex justify-between mt-2 text-xs font-data text-on-surface-variant/60">
                            <span>0%</span>
                            <span>100%</span>
                        </div>
                    </div>
                </div>

                <!-- Details Section -->
                <div class="editorial-border bg-white">
                    <div class="grid grid-cols-1 lg:grid-cols-2">
                        <!-- Drivers List -->
                        <div class="p-8 border-b lg:border-b-0 lg:border-r editorial-border">
                            <h4 class="text-xs font-bold text-on-surface-variant mb-6 uppercase tracking-widest">Primary Risk Drivers</h4>
                            <ul id="risk_drivers_list" class="space-y-4">
                                <li class="flex items-start">
                                    <span class="material-symbols-outlined text-error mr-3 mt-0.5 text-sm">priority_high</span>
                                    <div>
                                        <p class="text-sm font-medium text-on-background">High customer return history</p>
                                        <p class="font-data text-xs text-on-surface-variant/70 mt-1">2 returns in past order history</p>
                                    </div>
                                </li>
                                <li class="flex items-start">
                                    <span class="material-symbols-outlined text-tertiary-container mr-3 mt-0.5 text-sm">straighten</span>
                                    <div>
                                        <p class="text-sm font-medium text-on-background">Category fit variance</p>
                                        <p class="font-data text-xs text-on-surface-variant/70 mt-1">Clothing category has higher sizing return rate</p>
                                    </div>
                                </li>
                            </ul>
                        </div>

                        <!-- Action Callout -->
                        <div class="p-8 bg-surface-container/50">
                            <h4 class="text-xs font-bold text-primary mb-6 uppercase tracking-widest">Recommended Business Action</h4>
                            <div id="action_box" class="bg-primary-fixed/30 border-l-2 border-primary p-6 mt-4">
                                <span class="material-symbols-outlined text-primary mb-4">crisis_alert</span>
                                <p id="recommendation_text" class="font-headline text-xl text-primary font-medium leading-relaxed">
                                    Display sizing fit warning before checkout & offer instant exchange incentive.
                                </p>
                            </div>
                            <div class="mt-6 flex gap-4">
                                <button onclick="alert('Business trigger executed successfully!')" class="bg-primary text-on-primary text-xs font-bold px-6 py-3 uppercase tracking-wide hover:bg-primary-container transition-colors">Trigger Action</button>
                                <button onclick="alert('Rule override applied.')" class="border border-primary text-primary text-xs font-bold px-6 py-3 uppercase tracking-wide hover:bg-primary/5 transition-colors">Override</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</main>

<script>
function evaluateRisk() {
    const category = document.getElementById("product_category").value;
    const shipping = document.getElementById("shipping_type").value;
    const price = parseFloat(document.getElementById("price").value) || 49.99;
    const quantity = parseInt(document.getElementById("quantity").value) || 1;
    const discount_pct = parseFloat(document.getElementById("discount_pct").value) || 10;
    const seller_rating = parseFloat(document.getElementById("seller_rating").value) || 4.2;
    const previous_returns = parseInt(document.getElementById("previous_returns_count").value) || 0;
    const customer_tenure = parseInt(document.getElementById("customer_tenure_days").value) || 120;
    const is_prime = document.getElementById("is_prime_member").checked;

    const payload = {
        product_category: category,
        price: price,
        seller_rating: seller_rating,
        customer_tenure_days: customer_tenure,
        previous_returns_count: previous_returns,
        is_prime_member: is_prime,
        quantity: quantity,
        shipping_type: shipping,
        discount_applied: discount_pct / 100.0
    };

    fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => {
        if (!res.ok) throw new Error('API response error ' + res.status);
        return res.json();
    })
    .then(data => updateUI(data, payload))
    .catch(err => {
        // Local calculation fallback if API endpoint is external or offline
        calculateClientSide(payload);
    });
}

function calculateClientSide(p) {
    let base = 0.20;
    if (p.product_category === 'Clothing') base += 0.25;
    if (p.product_category === 'Electronics') base += 0.15;
    if (p.previous_returns_count >= 2) base += 0.30;
    else if (p.previous_returns_count === 1) base += 0.15;
    if (p.seller_rating < 3.8) base += 0.15;
    if (p.discount_applied >= 0.15) base += 0.10;
    if (p.customer_tenure_days < 60) base += 0.08;

    const prob = Math.min(0.98, Math.max(0.05, base));
    const score = Math.round(prob * 100);
    const tier = prob >= 0.65 ? "High Risk" : (prob >= 0.35 ? "Medium Risk" : "Low Risk");

    const factors = [];
    if (p.previous_returns_count >= 2) factors.append ? factors.push("High customer return history (" + p.previous_returns_count + " returns)") : null;
    if (p.product_category === 'Clothing') factors.push("Category 'Clothing' has higher baseline size fit return rate");
    if (p.seller_rating < 3.8) factors.push("Low seller rating (" + p.seller_rating + "/5.0) correlates with item mismatch");
    if (p.discount_applied >= 0.15) factors.push("Heavy discount (" + (p.discount_applied*100) + "%) increases impulse purchase return probability");
    if (factors.length === 0) factors.push("Standard order metrics with low risk profile");

    const rec = prob >= 0.65 
        ? "Display sizing fit warning before checkout & offer instant exchange incentive."
        : (prob >= 0.35 ? "Highlight clear return policy details & prompt for size confirmation." : "Standard checkout approved. Eligible for instant automated refund processing.");

    updateUI({
        return_probability: prob,
        risk_score: score,
        risk_tier: tier,
        risk_factors: factors,
        recommendation: rec
    }, p);
}

function updateUI(data, payload) {
    document.getElementById("risk_score_val").innerText = data.risk_score;
    document.getElementById("return_prob_val").innerText = (data.return_probability * 100).toFixed(1) + "%";

    const badge = document.getElementById("risk_tier_badge");
    const scoreVal = document.getElementById("risk_score_val");
    badge.innerText = data.risk_tier;

    if (data.risk_tier === "High Risk") {
        badge.className = "inline-block px-3 py-1 text-xs font-bold uppercase tracking-wider border border-error text-error bg-error/5";
        scoreVal.className = "font-headline text-6xl font-semibold text-error";
    } else if (data.risk_tier === "Medium Risk") {
        badge.className = "inline-block px-3 py-1 text-xs font-bold uppercase tracking-wider border border-amber-600 text-amber-700 bg-amber-50";
        scoreVal.className = "font-headline text-6xl font-semibold text-amber-600";
    } else {
        badge.className = "inline-block px-3 py-1 text-xs font-bold uppercase tracking-wider border border-emerald-600 text-emerald-700 bg-emerald-50";
        scoreVal.className = "font-headline text-6xl font-semibold text-emerald-600";
    }

    // Update segmented bar
    const bar = document.getElementById("segmented_bar");
    const segments = bar.children;
    const filledCount = Math.round(data.return_probability * 10);

    for (let i = 0; i < segments.length; i++) {
        if (i < filledCount) {
            segments[i].className = i >= 6 
                ? "h-full flex-1 bg-error transition-all duration-300" 
                : (i >= 3 ? "h-full flex-1 bg-amber-500 transition-all duration-300" : "h-full flex-1 bg-primary transition-all duration-300");
        } else {
            segments[i].className = "h-full flex-1 bg-outline-variant/30 transition-all duration-300";
        }
    }

    // Drivers
    const list = document.getElementById("risk_drivers_list");
    list.innerHTML = "";
    data.risk_factors.forEach(f => {
        const li = document.createElement("li");
        li.className = "flex items-start";
        li.innerHTML = `
            <span class="material-symbols-outlined text-primary mr-3 mt-0.5 text-sm">priority_high</span>
            <div>
                <p class="text-sm font-medium text-on-background">${f}</p>
            </div>
        `;
        list.appendChild(li);
    });

    // Recommendation
    document.getElementById("recommendation_text").innerText = data.recommendation;
}
</script>
</body>
</html>
"""

# Render full screen Google Stitch template in Streamlit
st.html(STITCH_HTML)

