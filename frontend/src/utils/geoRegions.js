/**
 * GlobeTrotter AI - Geographic Region & Category Resolution Engine.
 * Accurately maps worldwide countries to their respective continental regions
 * and normalizes travel categories for multi-filter combinatorial searches.
 */

export const COUNTRY_TO_REGION = {
  // North America
  'canada': 'North America',
  'united states': 'North America',
  'usa': 'North America',
  'united states of america': 'North America',
  'mexico': 'North America',

  // South America
  'peru': 'South America',
  'bolivia': 'South America',
  'brazil': 'South America',
  'chile': 'South America',
  'argentina': 'South America',
  'colombia': 'South America',
  'ecuador': 'South America',
  'venezuela': 'South America',
  'guyana': 'South America',
  'suriname': 'South America',
  'uruguay': 'South America',
  'paraguay': 'South America',
  'costa rica': 'South America',
  'panama': 'South America',
  'guatemala': 'South America',
  'belize': 'South America',
  'honduras': 'South America',

  // East & Southeast Asia
  'japan': 'East & Southeast Asia',
  'china': 'East & Southeast Asia',
  'south korea': 'East & Southeast Asia',
  'korea': 'East & Southeast Asia',
  'taiwan': 'East & Southeast Asia',
  'vietnam': 'East & Southeast Asia',
  'thailand': 'East & Southeast Asia',
  'indonesia': 'East & Southeast Asia',
  'bali': 'East & Southeast Asia',
  'laos': 'East & Southeast Asia',
  'cambodia': 'East & Southeast Asia',
  'philippines': 'East & Southeast Asia',
  'malaysia': 'East & Southeast Asia',
  'singapore': 'East & Southeast Asia',
  'myanmar': 'East & Southeast Asia',

  // South & Central Asia
  'india': 'South & Central Asia',
  'nepal': 'South & Central Asia',
  'sri lanka': 'South & Central Asia',
  'bhutan': 'South & Central Asia',
  'bangladesh': 'South & Central Asia',
  'pakistan': 'South & Central Asia',
  'maldives': 'South & Central Asia',
  'uzbekistan': 'South & Central Asia',
  'kazakhstan': 'South & Central Asia',
  'kyrgyzstan': 'South & Central Asia',
  'tajikistan': 'South & Central Asia',
  'turkmenistan': 'South & Central Asia',

  // Western & Northern Europe
  'austria': 'Western & Northern Europe',
  'germany': 'Western & Northern Europe',
  'france': 'Western & Northern Europe',
  'united kingdom': 'Western & Northern Europe',
  'uk': 'Western & Northern Europe',
  'england': 'Western & Northern Europe',
  'scotland': 'Western & Northern Europe',
  'wales': 'Western & Northern Europe',
  'ireland': 'Western & Northern Europe',
  'switzerland': 'Western & Northern Europe',
  'netherlands': 'Western & Northern Europe',
  'belgium': 'Western & Northern Europe',
  'luxembourg': 'Western & Northern Europe',
  'norway': 'Western & Northern Europe',
  'sweden': 'Western & Northern Europe',
  'denmark': 'Western & Northern Europe',
  'finland': 'Western & Northern Europe',
  'iceland': 'Western & Northern Europe',

  // Southern & Eastern Europe
  'italy': 'Southern & Eastern Europe',
  'greece': 'Southern & Eastern Europe',
  'spain': 'Southern & Eastern Europe',
  'portugal': 'Southern & Eastern Europe',
  'bulgaria': 'Southern & Eastern Europe',
  'croatia': 'Southern & Eastern Europe',
  'romania': 'Southern & Eastern Europe',
  'poland': 'Southern & Eastern Europe',
  'czech republic': 'Southern & Eastern Europe',
  'czechia': 'Southern & Eastern Europe',
  'hungary': 'Southern & Eastern Europe',
  'turkey': 'Southern & Eastern Europe',
  'serbia': 'Southern & Eastern Europe',
  'slovenia': 'Southern & Eastern Europe',
  'slovakia': 'Southern & Eastern Europe',
  'montenegro': 'Southern & Eastern Europe',
  'albania': 'Southern & Eastern Europe',
  'bosnia and herzegovina': 'Southern & Eastern Europe',
  'cyprus': 'Southern & Eastern Europe',
  'malta': 'Southern & Eastern Europe',

  // Middle East & North Africa
  'morocco': 'Middle East & North Africa',
  'egypt': 'Middle East & North Africa',
  'tunisia': 'Middle East & North Africa',
  'united arab emirates': 'Middle East & North Africa',
  'uae': 'Middle East & North Africa',
  'dubai': 'Middle East & North Africa',
  'jordan': 'Middle East & North Africa',
  'oman': 'Middle East & North Africa',
  'saudi arabia': 'Middle East & North Africa',
  'qatar': 'Middle East & North Africa',
  'israel': 'Middle East & North Africa',
  'lebanon': 'Middle East & North Africa',

  // Sub-Saharan Africa
  'kenya': 'Sub-Saharan Africa',
  'tanzania': 'Sub-Saharan Africa',
  'south africa': 'Sub-Saharan Africa',
  'namibia': 'Sub-Saharan Africa',
  'botswana': 'Sub-Saharan Africa',
  'rwanda': 'Sub-Saharan Africa',
  'uganda': 'Sub-Saharan Africa',
  'zimbabwe': 'Sub-Saharan Africa',
  'zambia': 'Sub-Saharan Africa',
  'madagascar': 'Sub-Saharan Africa',
  'ethiopia': 'Sub-Saharan Africa',
  'ghana': 'Sub-Saharan Africa',
  'senegal': 'Sub-Saharan Africa',

  // Oceania & Pacific Islands
  'australia': 'Oceania & Pacific Islands',
  'new zealand': 'Oceania & Pacific Islands',
  'fiji': 'Oceania & Pacific Islands',
  'french polynesia': 'Oceania & Pacific Islands',
  'tahiti': 'Oceania & Pacific Islands',
  'samoa': 'Oceania & Pacific Islands',
  'papua new guinea': 'Oceania & Pacific Islands',
};

/**
 * Resolves the standardized region for any post.
 */
export function resolvePostRegion(post) {
  if (!post) return 'Global';
  
  // 1. If backend already resolved a recognized region
  if (post.region && post.region !== 'Global' && post.region !== 'World') {
    return post.region;
  }

  // 2. Resolve via country name
  const rawCountry = (post.country || '').toLowerCase().trim();
  if (COUNTRY_TO_REGION[rawCountry]) {
    return COUNTRY_TO_REGION[rawCountry];
  }

  // 3. Substring matching across known countries
  for (const [countryKey, regionName] of Object.entries(COUNTRY_TO_REGION)) {
    if (rawCountry.includes(countryKey) || countryKey.includes(rawCountry)) {
      return regionName;
    }
  }

  // 4. Check destination name for country/region clues
  const rawDest = (post.destination || '').toLowerCase();
  for (const [countryKey, regionName] of Object.entries(COUNTRY_TO_REGION)) {
    if (rawDest.includes(countryKey)) {
      return regionName;
    }
  }

  return 'Global';
}

/**
 * Normalizes travel categories so that shorthand categories like
 * "Heritage" or "Mountains & Natural Wonders" match "Historical Monuments & Heritage Sites"
 * or "Waterfalls, Mountains & Natural Wonders".
 */
export function isCategoryMatch(postCategory, targetCategory) {
  if (!targetCategory || targetCategory === 'All Categories') return true;
  if (!postCategory) return false;

  const p = postCategory.toLowerCase().trim();
  const t = targetCategory.toLowerCase().trim();

  // Exact match
  if (p === t) return true;

  // Normalized theme groups
  if (t.includes('waterfall') || t.includes('mountain') || t.includes('natural')) {
    return p.includes('waterfall') || p.includes('mountain') || p.includes('natural') || p.includes('nature');
  }
  if (t.includes('monument') || t.includes('heritage') || t.includes('ancient')) {
    return p.includes('monument') || p.includes('heritage') || p.includes('historic') || p.includes('ancient');
  }
  if (t.includes('cuisine') || t.includes('culinary') || t.includes('food')) {
    return p.includes('cuisine') || p.includes('culinary') || p.includes('food') || p.includes('dining') || p.includes('pasta');
  }
  if (t.includes('wildlife') || t.includes('safari') || t.includes('national park')) {
    return p.includes('wildlife') || p.includes('safari') || p.includes('park') || p.includes('birdwatching') || p.includes('animal');
  }
  if (t.includes('coastal') || t.includes('island') || t.includes('beach')) {
    return p.includes('coastal') || p.includes('island') || p.includes('beach') || p.includes('sea') || p.includes('caldera');
  }
  if (t.includes('hidden gem') || t.includes('unexplored')) {
    return p.includes('hidden') || p.includes('gem') || p.includes('unexplored');
  }
  if (t.includes('road trip') || t.includes('itinerary')) {
    return p.includes('road trip') || p.includes('scenic') || p.includes('itinerary') || p.includes('drive');
  }
  if (t.includes('festival') || t.includes('tradition') || t.includes('culture')) {
    return p.includes('festival') || p.includes('tradition') || p.includes('culture') || p.includes('cultural');
  }
  if (t.includes('experience') || t.includes('immersive')) {
    return p.includes('experience') || p.includes('immersive') || p.includes('activity') || p.includes('living history');
  }

  return p.includes(t) || t.includes(p);
}

/**
 * Validates whether an article's publication or creation date matches
 * the selected date filter ('all', 'today', 'week', 'month', or 'custom').
 */
export function isDateMatch(dateStr, dateFilter = 'all', customDate = null) {
  if (!dateFilter || dateFilter === 'all' || dateFilter === 'All Dates') return true;
  if (!dateStr) return false;

  const postDate = new Date(dateStr);
  if (isNaN(postDate.getTime())) return false;

  const now = new Date();
  const diffMs = now.getTime() - postDate.getTime();
  const diffDays = diffMs / (1000 * 60 * 60 * 24);

  if (dateFilter === 'today' || dateFilter === 'Today') {
    // Check if published on the same calendar day or within the last 24 hours
    const isSameDay = (
      postDate.getFullYear() === now.getFullYear() &&
      postDate.getMonth() === now.getMonth() &&
      postDate.getDate() === now.getDate()
    );
    const isSameUTCDay = (
      postDate.getUTCFullYear() === now.getUTCFullYear() &&
      postDate.getUTCMonth() === now.getUTCMonth() &&
      postDate.getUTCDate() === now.getUTCDate()
    );
    return isSameDay || isSameUTCDay || (diffDays >= 0 && diffDays <= 1.0);
  }

  if (dateFilter === 'week' || dateFilter === 'This Week' || dateFilter === 'Past 7 Days') {
    return diffDays >= -0.5 && diffDays <= 7.0;
  }

  if (dateFilter === 'month' || dateFilter === 'This Month' || dateFilter === 'Past 30 Days') {
    return diffDays >= -0.5 && diffDays <= 30.0;
  }

  if (dateFilter === 'custom' && customDate) {
    const postDateYMD = postDate.toISOString().slice(0, 10);
    const postLocalDate = `${postDate.getFullYear()}-${String(postDate.getMonth() + 1).padStart(2, '0')}-${String(postDate.getDate()).padStart(2, '0')}`;
    return postDateYMD === customDate || postLocalDate === customDate;
  }

  return true;
}

/**
 * Combinatorial Filter: matches post against Region AND Category AND Date AND Search Query (Strict Boolean AND).
 */
export function matchesCombinatorialFilter(
  post, 
  selectedRegion, 
  selectedCategory, 
  selectedDateFilter = 'all', 
  searchQuery = '', 
  customDate = null
) {
  // 1. Search Query
  const q = searchQuery.toLowerCase().trim();
  const matchesSearch = !q || (
    post.title?.toLowerCase().includes(q) ||
    post.destination?.toLowerCase().includes(q) ||
    post.country?.toLowerCase().includes(q) ||
    post.summary?.toLowerCase().includes(q) ||
    post.category?.toLowerCase().includes(q)
  );
  if (!matchesSearch) return false;

  // 2. Region Filter (AND logic)
  if (selectedRegion && selectedRegion !== 'All Regions') {
    const postRegion = resolvePostRegion(post);
    if (postRegion !== selectedRegion) {
      return false;
    }
  }

  // 3. Category Filter (AND logic)
  if (selectedCategory && selectedCategory !== 'All Categories') {
    if (!isCategoryMatch(post.category, selectedCategory)) {
      return false;
    }
  }

  // 4. Date Filter (AND logic)
  const dateStr = post.published_at || post.created_at;
  if (!isDateMatch(dateStr, selectedDateFilter, customDate)) {
    return false;
  }

  return true;
}
