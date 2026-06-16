// app.js — clean, single-file implementation
// Provides: TRANSLATIONS, i18n helper, fetchAPI, MealIcons, logout

const BACKEND_HOSTS = ['127.0.0.1:8000', 'localhost:8000'];
const BACKEND_API_BASE = 'http://127.0.0.1:8000/api/';
const API_BASE = (location.protocol === 'file:' || location.origin === 'null' || !BACKEND_HOSTS.includes(location.host))
  ? BACKEND_API_BASE
  : '/api/';

const TRANSLATIONS = {
  en: {
    // App & navigation
    logo: "NutriTracker",
    dashboard: "Dashboard",
    meals: "Meals",
    water: "Water",
    bmi: "BMI",
    progress: "Progress",
    assistant: "Health Assistant",
    logout: "Logout",

    // Dashboard
    dashboard_title: "Dashboard",
    calories_left: "Calories Left",
    water_glasses: "Water Glasses",
    meals_today: "Meals Today",
    bmi_label: "BMI",
    calorie_goal: "Daily Calorie Goal",
    consumed: "Consumed",
    remaining: "remaining",
    water_consumed: "glasses consumed",
    calories_remaining: "calories remaining",
    of: "of",

    // Meals
    meal_tracking: "Meal Tracking",
    total_calories_today: "Total: {cal} calories today",
    add_meal: "+ Add Meal",
    name: "Name",
    type: "Type",
    time: "Time",
    calories: "Calories",
    calories_auto: "Calories (auto-calculated)",
    protein_g: "Protein (g)",
    protein: "Protein",
    cancel: "Cancel",
    add: "Add",
    log_meal: "Log Meal",
    image_rec: "Image Food Recognition",
    voice_log: "Voice Food Logging",
    upload_desc: "Upload or drag & drop a food image here to auto-detect calories & nutrients.",
    analyze_btn: "Analyze Image",
    analyzing: "Analyzing...",
    click_mic: "Click the microphone and start speaking...",
    listening: "Listening...",
    logged_via_voice: "Logged via voice!",
    no_foods_detected: "No foods detected. Try again.",
    confidence: "Confidence",
    detected: "Detected",

    // Water page
    water_title: "Water Intake Tracker",
    glasses: "glasses",
    more_glasses_goal: "{left} more glasses to reach your goal",
    goal_reached: "Goal reached! Great job 🎉",
    complete: "Complete",
    todays_progress: "Today's Progress",
    hydration_tip: "💧 Hydration Tip",
    hydration_desc: "Drink a glass of water first thing in the morning to kick-start your metabolism and rehydrate after sleep.",

    // BMI
    bmi_title: "BMI Calculator",
    calculate_bmi: "Calculate Your BMI",
    height: "Height (cm)",
    weight: "Weight (kg)",
    calc_btn: "Calculate BMI",
    saved_dashboard: "Your BMI has been saved to your dashboard.",
    enter_stats: "Enter your height and weight to calculate your BMI",
    about_bmi_title: "About BMI",
    about_bmi_desc1: "Body Mass Index (BMI) is a measure of body fat based on height and weight.",
    about_bmi_desc2: "For a comprehensive health assessment, consult with a healthcare professional.",
    underweight: "Underweight",
    normal_weight: "Normal weight",
    overweight: "Overweight",
    obese: "Obese",

    // Progress / analytics
    progress_title: "Progress & Analytics",
    weekly_avg_cal: "Weekly Avg Calories",
    weekly_avg_water: "Weekly Avg Water",
    current_bmi: "Current BMI",
    days_on_track: "Days on Track",
    weekly_calorie: "Weekly Calorie Intake",
    weekly_water: "Weekly Water Intake",
    bmi_trend: "BMI Trend (Weekly)",

    // Auth
    login_title: "Login - NutriTracker",
    signup_title: "Sign Up - NutriTracker",
    username: "Username",
    email: "Email",
    password: "Password",
    login_btn: "Login",
    signup_btn: "Sign Up",
    dont_have_acct: "Don't have an account?",
    already_have_acct: "Already have an account?",
    tagline: "Track your nutrition, stay healthy"
  },
  kn: {
    logo: "NutriTracker",
    dashboard: "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
    meals: "ಭೋಜನಗಳು",
    water: "ನೀರು",
    bmi: "BMI",
    progress: "ಪ್ರಗತಿ",
    logout: "ಲಾಗ್‌ಔಟ್",
    dashboard_title: "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
    calories_left: "ಉಳಿದ ಕ್ಯಾಲೊರಿಗಳು",
    water_glasses: "ನೀರಿನ ಗ್ಲಾಸುಗಳು",
    meals_today: "ಇಂದಿನ ಭೋಜನ",
    bmi_label: "BMI",
    calorie_goal: "ದೈನಂದಿನ ಕ್ಯಾಲೊರಿ ಗುರಿ",
    consumed: "ಸೇವಿಸಿದ",
    remaining: "ಉಳಿದಿದೆ",
    calories_remaining: "ಕ್ಯಾಲೊರಿ ಉಳಿದಿದೆ",
    water_consumed: "ಗ್ಲಾಸ್ ಕುಡಿದಿದ್ದೀರಿ",
    of: "ರಲ್ಲಿ",
    glasses: "ಗ್ಲಾಸ್",
    more_glasses_goal: "ಗುರಿ ತಲುಪಲು {left} ಗ್ಲಾಸ್ ಹೆಚ್ಚು",
    goal_reached: "ಗುರಿ ತಲುಪಿದ್ದೀರಿ! ಅದ್ಭುತ 🎉",
    complete: "ಪೂರ್ಣ",
    meal_tracking: "ಭೋಜನ ಟ್ರ್ಯಾಕಿಂಗ್",
    total_calories_today: "ಒಟ್ಟು: ಇಂದು {cal} ಕ್ಯಾಲೊರಿ",
    add_meal: "+ ಭೋಜನ ಸೇರಿಸಿ",
    name: "ಹೆಸರು",
    type: "ವಿಧ",
    time: "ಸಮಯ",
    calories: "ಕ್ಯಾಲೊರಿ",
    calories_auto: "ಕ್ಯಾಲೊರಿ (ಸ್ವಯಂ ಲೆಕ್ಕ)",
    protein_g: "ಪ್ರೊಟೀನ್ (ಗ್ರಾಂ)",
    protein: "ಪ್ರೊಟೀನ್",
    cancel: "ರದ್ದು",
    add: "ಸೇರಿಸಿ",
    log_meal: "ದಾಖಲಿಸಿ",
    image_rec: "ಚಿತ್ರದಿಂದ ಆಹಾರ ಗುರುತಿಸುವಿಕೆ",
    voice_log: "ಧ್ವನಿಯಿಂದ ಆಹಾರ ದಾಖಲಿಸಿ",
    upload_desc: "ಆಹಾರದ ಚಿತ್ರ ಅಪ್ಲೋಡ್ ಮಾಡಿ ಅಥವಾ ಎಳೆಯಿರಿ.",
    analyze_btn: "ಚಿತ್ರ ವಿಶ್ಲೇಷಣೆ",
    analyzing: "ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ...",
    click_mic: "ಮೈಕ್ ಕ್ಲಿಕ್ ಮಾಡಿ ಮಾತನಾಡಿ...",
    listening: "ಕೇಳುತ್ತಿದ್ದೇವೆ...",
    logged_via_voice: "ಧ್ವನಿಯಿಂದ ದಾಖಲಾಯಿತು!",
    no_foods_detected: "ಆಹಾರ ಪತ್ತೆಯಾಗಲಿಲ್ಲ. ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
    confidence: "ನಿಖರತೆ",
    detected: "ಪತ್ತೆಯಾಗಿದೆ",
    water_title: "ನೀರಿನ ಬಳಕೆ ಟ್ರ್ಯಾಕರ್",
    todays_progress: "ಇಂದಿನ ಪ್ರಗತಿ",
    hydration_tip: "💧 ಹೈಡ್ರೇಶನ್ ಸಲಹೆ",
    hydration_desc: "ಬೆಳಿಗ್ಗೆ ಮೊದಲು ಒಂದು ಗ್ಲಾಸ್ ನೀರು ಕುಡಿಯಿರಿ - ಇದು ನಿಮ್ಮ ಚಯಾಪಚಯ ಕ್ರಿಯೆಯನ್ನು ಸಕ್ರಿಯಗೊಳಿಸುತ್ತದೆ.",
    bmi_title: "BMI ಕ್ಯಾಲ್ಕುಲೇಟರ್",
    calculate_bmi: "ನಿಮ್ಮ BMI ಲೆಕ್ಕ ಹಾಕಿ",
    height: "ಎತ್ತರ (ಸೆಂ.ಮೀ)",
    weight: "ತೂಕ (ಕೆ.ಜಿ)",
    calc_btn: "BMI ಲೆಕ್ಕ ಹಾಕಿ",
    progress_title: "ಪ್ರಗತಿ ಮತ್ತು ವಿಶ್ಲೇಷಣೆ",
    weekly_avg_cal: "ಸಾಪ್ತಾಹಿಕ ಸರಾಸರಿ ಕ್ಯಾಲೊರಿ",
    weekly_avg_water: "ಸಾಪ್ತಾಹಿಕ ಸರಾಸರಿ ನೀರು",
    current_bmi: "ಪ್ರಸ್ತುತ BMI",
    days_on_track: "ಗುರಿ ತಲುಪಿದ ದಿನಗಳು",
    saved_dashboard: "ನಿಮ್ಮ BMI ಅನ್ನು ಡ್ಯಾಶ್‌ಬೋರ್ಡ್‌ಗೆ ಉಳಿಸಲಾಗಿದೆ.",
    enter_stats: "ನಿಮ್ಮ BMI ಲೆಕ್ಕ ಹಾಕಲು ಎತ್ತರ ಮತ್ತು ತೂಕ ನಮೂದಿಸಿ",
    about_bmi_title: "BMI ಬಗ್ಗೆ",
    about_bmi_desc1: "ಬಾಡಿ ಮಾಸ್ ಇಂಡೆಕ್ಸ್ (BMI) ಎತ್ತರ ಮತ್ತು ತೂಕದ ಆಧಾರದ ಮೇಲೆ ದೇಹದ ಕೊಬ್ಬಿನ ಅಳತೆ.",
    about_bmi_desc2: "ಸಮಗ್ರ ಆರೋಗ್ಯ ಮೌಲ್ಯಮಾಪನಕ್ಕಾಗಿ, ಆರೋಗ್ಯ ವೃತ್ತಿಪರರೊಂದಿಗೆ ಸಂಪರ್ಕಿಸಿ.",
    underweight: "ಕಡಿಮೆ ತೂಕ",
    normal_weight: "ಸಾಮಾನ್ಯ ತೂಕ",
    overweight: "ಹೆಚ್ಚು ತೂಕ",
    obese: "ಸ್ಥೂಲತೆ",
    weekly_calorie: "ಸಾಪ್ತಾಹಿಕ ಕ್ಯಾಲೊರಿ ಸೇವನೆ",
    weekly_water: "ಸಾಪ್ತಾಹಿಕ ನೀರಿನ ಸೇವನೆ",
    bmi_trend: "BMI ಪ್ರವೃತ್ತಿ (ವಾರದ)",
    login_title: "ಲಾಗಿನ್ - NutriTracker",
    signup_title: "ಸೈನ್ ಅಪ್ - NutriTracker",
    username: "ಬಳಕೆದಾರ ಹೆಸರು",
    email: "ಇಮೇಲ್",
    password: "ಪಾಸ್‌ವರ್ಡ್",
    login_btn: "ಲಾಗಿನ್",
    signup_btn: "ಸೈನ್ ಅಪ್",
    dont_have_acct: "ಖಾತೆ ಇಲ್ಲವೇ?",
    already_have_acct: "ಈಗಾಗಲೇ ಖಾತೆ ಇದೆಯೇ?",
    tagline: "ನಿಮ್ಮ ಪೌಷ್ಟಿಕಾಂಶವನ್ನು ಟ್ರ್ಯಾಕ್ ಮಾಡಿ, ಆರೋಗ್ಯವಾಗಿರಿ"
  },
  te: {
    logo: "NutriTracker",
    dashboard: "డాష్‌బోర్డ్",
    meals: "ఆహారాలు",
    water: "నీరు",
    bmi: "BMI",
    progress: "ప్రగతి",
    logout: "లాగ్ అవుట్",
    dashboard_title: "డాష్‌బోర్డ్",
    calories_left: "మిగిలిన కేలరీలు",
    water_glasses: "నీటి గ్లాసులు",
    meals_today: "నేటి భోజనాలు",
    bmi_label: "BMI",
    calorie_goal: "రోజువారీ కేలరీ లక్ష్యం",
    consumed: "తీసుకున్నారు",
    remaining: "మిగిలింది",
    calories_remaining: "కేలరీలు మిగిలి ఉన్నాయి",
    water_consumed: "గ్లాసులు తాగారు",
    of: "లో",
    glasses: "గ్లాసులు",
    more_glasses_goal: "లక్ష్యానికి {left} గ్లాసులు అవసరం",
    goal_reached: "లక్ష్యం చేరుకున్నారు! అభినందనలు 🎉",
    complete: "పూర్తి",
    meal_tracking: "భోజన ట్రాకింగ్",
    total_calories_today: "మొత్తం: నేడు {cal} కేలరీలు",
    add_meal: "+ భోజనం జోడించు",
    name: "పేరు",
    type: "రకం",
    time: "సమయం",
    calories: "కేలరీలు",
    calories_auto: "కేలరీలు (స్వయంచాలక లెక్క)",
    protein_g: "ప్రొటీన్ (గ్రా)",
    protein: "ప్రొటీన్",
    cancel: "రద్దు చేయి",
    add: "జోడించు",
    log_meal: "నమోదు చేయి",
    image_rec: "చిత్రం ద్వారా ఆహారం గుర్తించడం",
    voice_log: "గళం ద్వారా ఆహారం నమోదు",
    upload_desc: "కేలరీలు తెలుసుకోవడానికి ఆహార చిత్రం అప్లోడ్ చేయండి.",
    analyze_btn: "చిత్రం విశ్లేషించు",
    analyzing: "విశ్లేషిస్తున్నారు...",
    click_mic: "మైక్ క్లిక్ చేసి మాట్లాడండి...",
    listening: "వింటున్నాం...",
    logged_via_voice: "గళం ద్వారా నమోదైంది!",
    no_foods_detected: "ఆహారం గుర్తించబడలేదు. మళ్లీ ప్రయత్నించండి.",
    confidence: "నిర్దుష్టత",
    detected: "గుర్తించబడింది",
    water_title: "నీటి వినియోగ ట్రాకర్",
    todays_progress: "నేటి పురోగతి",
    hydration_tip: "💧 హైడ్రేషన్ సలహా",
    hydration_desc: "ఉదయం లేవగానే ఒక గ్లాసు నీళ్ళు తాగండి - ఇది మీ జీవక్రియను క్రియాశీలంగా ఉంచుతుంది.",
    bmi_title: "BMI కాలిక్యులేటర్",
    calculate_bmi: "మీ BMI లెక్కించండి",
    height: "ఎత్తు (సె.మీ)",
    weight: "బరువు (కె.జి)",
    calc_btn: "BMI లెక్కించు",
    progress_title: "పురోగతి & విశ్లేషణలు",
    weekly_avg_cal: "వారపు సగటు కేలరీలు",
    weekly_avg_water: "వారపు సగటు నీరు",
    current_bmi: "ప్రస్తుత BMI",
    days_on_track: "లక్ష్యంలో ఉన్న రోజులు",
    saved_dashboard: "మీ BMI మీ డాష్‌బోర్డ్‌లో సేవ్ చేయబడింది.",
    enter_stats: "మీ BMI లెక్కించడానికి మీ ఎత్తు మరియు బరువు నమోదు చేయండి",
    about_bmi_title: "BMI గురించి",
    about_bmi_desc1: "బాడీ మాస్ ఇండెక్స్ (BMI) అనేది ఎత్తు మరియు బరువు ఆధారంగా శరీర కొవ్వు కొలమానం.",
    about_bmi_desc2: "సమగ్ర ఆరోగ్య అంచనా కోసం, ఆరోగ్య సంరక్షకుడితో సంప్రదించండి.",
    underweight: "తక్కువ బరువు",
    normal_weight: "సాధారణ బరువు",
    overweight: "అధిక బరువు",
    obese: "స్థూలత",
    weekly_calorie: "వారపు కేలరీ సేవన",
    weekly_water: "వారపు నీటి సేవన",
    bmi_trend: "BMI ధోరణి (వారపు)",
    login_title: "లాగిన్ - NutriTracker",
    signup_title: "సైన్ అప్ - NutriTracker",
    username: "వినియోగదారు పేరు",
    email: "ఇమెయిల్",
    password: "పాస్‌వర్డ్",
    login_btn: "లాగిన్",
    signup_btn: "సైన్ అప్",
    dont_have_acct: "ఖాతా లేదా?",
    already_have_acct: "ఇప్పటికే ఖాతా ఉందా?",
    tagline: "మీ పోషకాహారాన్ని ట్రాక్ చేయండి, ఆరోగ్యంగా ఉండండి"
  },
  ta: {
    logo: "NutriTracker",
    dashboard: "டாஷ்போர்ட்",
    meals: "உணவுகள்",
    water: "தண்ணீர்",
    bmi: "BMI",
    progress: "முன்னேறல்",
    logout: "லாக்அவுட்",
    dashboard_title: "டாஷ்போர்ட்",
    calories_left: "மீதமுள்ள கலோரிகள்",
    water_glasses: "தண்ணீர் கண்ணாடிகள்",
    meals_today: "இன்றைய உணவுகள்",
    bmi_label: "BMI",
    calorie_goal: "தினசரி கலோரி இலக்கு",
    consumed: "உட்கொண்டது",
    remaining: "மீதம்",
    water_consumed: "கண்ணாடிகள் குடித்தது",
    calories_remaining: "கலோரிகள் மீதமுள்ளன",
    of: "இல்",
    glasses: "கண்ணாடிகள்",
    more_glasses_goal: "இலக்கை அடைய {left} கண்ணாடிகள் மேலும்",
    goal_reached: "இலக்கை அடைந்துவிட்டீர்கள்! சிறப்பு 🎉",
    complete: "முடிந்தது",
    meal_tracking: "உணவு கண்காணிப்பு",
    total_calories_today: "மொத்தம்: இன்று {cal} கலோரிகள்",
    add_meal: "+ உணவு சேர்",
    name: "பெயர்",
    type: "வகை",
    time: "நேரம்",
    calories: "கலோரிகள்",
    calories_auto: "கலோரிகள் (தானாக கணக்கிடப்பட்டது)",
    protein_g: "புரதம் (கிராம்)",
    protein: "புரதம்",
    cancel: "ரத்து செய்",
    add: "சேர்",
    log_meal: "உணவு பதிவு",
    image_rec: "பட உணவு அடையாளம்",
    voice_log: "குரல் உணவு பதிவு",
    upload_desc: "கலோரிகள் மற்றும் ஊட்டச்சத்துகளை தானாகக் கண்டறிய உணவு படத்தை பதிவேற்றவும்.",
    analyze_btn: "படத்தை பகுப்பாய்வு செய்",
    analyzing: "பகுப்பாய்வு செய்கிறது...",
    click_mic: "மைக்ரோஃபோனை கிளிக் செய்து பேசத் தொடங்கவும்...",
    listening: "கேட்கிறோம்...",
    logged_via_voice: "குரல் வழியாக பதிவு செய்யப்பட்டது!",
    no_foods_detected: "உணவுகள் கண்டறியப்படவில்லை. மீண்டும் முயற்சி செய்யவும்.",
    confidence: "நம்பிக்கை",
    detected: "கண்டறியப்பட்டது",
    water_title: "தண்ணீர் உட்கொள்ளல் கண்காணிப்பு",
    todays_progress: "இன்றைய முன்னேற்றம்",
    hydration_tip: "💧 நீரேற்ற குறிப்பு",
    hydration_desc: "காலையில் முதலில் ஒரு கண்ணாடி தண்ணீர் குடிக்கவும் - இது உங்கள் வளர்ச்சித்திறனைத் தூண்டுகிறது.",
    bmi_title: "BMI கணக்கிடுபவர்",
    calculate_bmi: "உங்கள் BMI ஐ கணக்கிடுங்கள்",
    height: "உயரம் (செ.மீ)",
    weight: "எடை (கிலோ)",
    calc_btn: "BMI கணக்கிடு",
    saved_dashboard: "உங்கள் BMI உங்கள் டாஷ்போர்டில் சேமிக்கப்பட்டது.",
    enter_stats: "உங்கள் BMI ஐ கணக்கிட உங்கள் உயரம் மற்றும் எடையை உள்ளிடவும்",
    about_bmi_title: "BMI பற்றி",
    about_bmi_desc1: "உடல் எடை குறியீடு (BMI) என்பது உயரம் மற்றும் எடையின் அடிப்படையில் உடல் கொழுத்தின் அளவீடு.",
    about_bmi_desc2: "முழுமையான சுகாதார மதிப்பீட்டிற்கு, சுகாதார நிபுணரை ஆலோசனை கேளுங்கள்.",
    underweight: "குறைந்த எடை",
    normal_weight: "இயல்பான எடை",
    overweight: "அதிக எடை",
    obese: "ஊட்டச்சத்து குறைபாடு",
    weekly_calorie: "வாராந்திர கலோரி உட்கொள்ளல்",
    weekly_water: "வாராந்திர தண்ணீர் உட்கொள்ளல்",
    bmi_trend: "BMI போக்கு (வாராந்திர)",
    progress_title: "முன்னேற்றம் மற்றும் பகுப்பாய்வு",
    weekly_avg_cal: "வாராந்திர சராசரி கலோரிகள்",
    weekly_avg_water: "வாராந்திர சராசரி தண்ணீர்",
    current_bmi: "தற்போதைய BMI",
    days_on_track: "இலக்கில் உள்ள நாட்கள்",
    login_title: "உள்நுழை - NutriTracker",
    signup_title: "பதிவு செய் - NutriTracker",
    username: "பயனர்பெயர்",
    email: "மின்னஞ்சல்",
    password: "கடவுச்சொல்",
    login_btn: "உள்நுழை",
    signup_btn: "பதிவு செய்",
    dont_have_acct: "கணக்கு இல்லையா?",
    already_have_acct: "ஏற்கனவே கணக்கு உள்ளதா?",
    tagline: "உங்கள் ஊட்டச்சத்தை கண்காணிக்கவும், ஆரோக்கியமாக இருங்கள்"
  },
  hi: {
    logo: "न्यूट्रिट्रैकर",
    dashboard: "डैशबोर्ड",
    meals: "भोजन",
    water: "पानी",
    bmi: "बीएमआई",
    progress: "प्रगति",
    logout: "लॉगआउट",
    dashboard_title: "डैशबोर्ड",
    calories_left: "बची हुई कैलोरी",
    water_glasses: "पानी के गिलास",
    meals_today: "आज का भोजन",
    bmi_label: "बीएमआई",
    calorie_goal: "दैनिक कैलोरी लक्ष्य",
    consumed: "खाया गया",
    remaining: "शेष",
    water_consumed: "गिलास पिए गए",
    calories_remaining: "कैलोरी शेष हैं",
    of: "में",
    glasses: "गिलास",
    more_glasses_goal: "लक्ष्य तक पहुंचने के लिए {left} गिलास और",
    goal_reached: "लक्ष्य हासिल! बहुत अच्छा 🎉",
    complete: "पूर्ण",
    meal_tracking: "भोजन ट्रैकिंग",
    total_calories_today: "कुल: आज {cal} कैलोरी",
    add_meal: "+ भोजन जोड़ें",
    name: "नाम",
    type: "प्रकार",
    time: "समय",
    calories: "कैलोरी",
    calories_auto: "कैलोरी (स्वचालित गणना)",
    protein_g: "प्रोटीन (ग्राम)",
    protein: "प्रोटीन",
    cancel: "रद्द करें",
    add: "जोड़ें",
    log_meal: "भोजन दर्ज करें",
    image_rec: "छवि खाद्य पहचान",
    voice_log: "आवाज खाद्य लॉगिंग",
    upload_desc: "कैलोरी और पोषक तत्वों को स्वचालित रूप से पहचानने के लिए खाद्य छवि अपलोड करें.",
    analyze_btn: "छवि का विश्लेषण करें",
    analyzing: "विश्लेषण हो रहा है...",
    click_mic: "माइक पर क्लिक करें और बोलना शुरू करें...",
    listening: "सुन रहा है...",
    logged_via_voice: "आवाज से लॉग हो गया!",
    no_foods_detected: "कोई खाद्य पदार्थ नहीं मिला. पुनः प्रयास करें.",
    confidence: "विश्वास",
    detected: "पता चला",
    water_title: "पानी का सेवन ट्रैकर",
    todays_progress: "आज की प्रगति",
    hydration_tip: "💧 हाइड्रेशन सलाह",
    hydration_desc: "सुबह उठकर सबसे पहले एक गिलास पानी पीने से आपके चयापचय को बढ़ावा मिलता है.",
    bmi_title: "BMI कैलकुलेटर",
    calculate_bmi: "अपना BMI की गणना करें",
    height: "ऊंचाई (सेमी)",
    weight: "वजन (किग्रा)",
    calc_btn: "BMI की गणना करें",
    saved_dashboard: "आपका BMI आपके डैशबोर्ड पर सहेज दिया गया है.",
    enter_stats: "अपना BMI की गणना करने के लिए अपनी ऊंचाई और वजन दर्ज करें",
    about_bmi_title: "BMI के बारे में",
    about_bmi_desc1: "बॉडी मास इंडेक्स (BMI) ऊंचाई और वजन के आधार पर शरीर के वसा का माप है.",
    about_bmi_desc2: "व्यापक स्वास्थ्य मूल्यांकन के लिए, किसी स्वास्थ्य देखभाल पेशेवर से परामर्श करें.",
    underweight: "कम वजन",
    normal_weight: "सामान्य वजन",
    overweight: "अधिक वजन",
    obese: "मोटापा",
    weekly_calorie: "साप्ताहिक कैलोरी सेवन",
    weekly_water: "साप्ताहिक पानी सेवन",
    bmi_trend: "BMI रुझान (साप्ताहिक)",
    progress_title: "प्रगति और विश्लेषण",
    weekly_avg_cal: "साप्ताहिक औसत कैलोरी",
    weekly_avg_water: "साप्ताहिक औसत पानी",
    current_bmi: "वर्तमान BMI",
    days_on_track: "लक्ष्य पर दिन",
    login_title: "लॉगिन - NutriTracker",
    signup_title: "साइन अप - NutriTracker",
    username: "उपयोगकर्ता नाम",
    email: "ईमेल",
    password: "पासवर्ड",
    login_btn: "लॉगिन",
    signup_btn: "साइन अप",
    dont_have_acct: "खाता नहीं है?",
    already_have_acct: "पहले से खाता है?",
    tagline: "अपने पोषण को ट्रैक करें, स्वस्थ रहें"
  }
};

const i18n = {
  lang: localStorage.getItem('lang') || (navigator.language || 'en').slice(0,2),
  t(key, vars) {
    const L = TRANSLATIONS[this.lang] || TRANSLATIONS.en;
    let v = L[key] || TRANSLATIONS.en[key] || key;
    if (vars) for (const k in vars) v = v.replace(new RegExp('\{'+k+'\}','g'), vars[k]);
    return v;
  },
  set(lang) {
    this.lang = lang;
    localStorage.setItem('lang', lang);
    this.translate();
  },
  translate() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      el.textContent = this.t(key);
    });
  }
};

async function fetchAPI(endpoint, opts = {}) {
  const token = localStorage.getItem('token');
  const url = endpoint.startsWith('http') ? endpoint : API_BASE + endpoint;
  const isFormData = opts.body instanceof FormData;
  
  // For FormData, let the browser set Content-Type automatically with the correct boundary
  // For JSON requests, explicitly set Content-Type
  const headers = Object.assign({}, opts.headers || {});
  if (!isFormData && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }
  if (token) {
    headers['Authorization'] = 'Bearer ' + token;
  }
  
  // Build the fetch options carefully
  const fetchOpts = {
    method: opts.method || 'GET',
    headers: headers,
    body: opts.body
  };
  
  // Remove body for GET requests or if body is undefined/null
  if (fetchOpts.method === 'GET' || fetchOpts.body === undefined || fetchOpts.body === null) {
    delete fetchOpts.body;
  }
  
  console.log('fetchAPI:', fetchOpts.method, url, isFormData ? '(FormData)' : '(JSON)');
  
  try {
    const res = await fetch(url, fetchOpts);
    console.log('fetchAPI response status:', res.status);
    
    if (res.status === 401) {
      localStorage.removeItem('token');
      window.location.href = 'login.html';
      return null;
    }
    
    const text = await res.text();
    console.log('fetchAPI response body:', text.substring(0, 500));
    
    try { return JSON.parse(text); } catch { return text; }
  } catch (e) {
    console.error('fetchAPI error:', e);
    throw e;
  }
}

const MealIcons = {
  coffee: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 8h1a4 4 0 0 1 0 8h-1M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4V8z"/><line x1="6" y1="2" x2="6" y2="4"/><line x1="10" y1="2" x2="10" y2="4"/><line x1="14" y1="2" x2="14" y2="4"/></svg>',
  sun: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>',
  apple: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 6c1-2 3-3 5-3 0 2-1 4-3 5M12 22c-4 0-7-3-7-7 0-4 3-6 6-6 1 0 2 .3 2.5.7.5-.4 1.5-.7 2.5-.7 3 0 6 2 6 6 0 4-3 7-7 7"/></svg>'
};

function logout() {
  console.log('Logout function called');
  localStorage.removeItem('token');
  localStorage.removeItem('nutri_state');
  window.location.href = 'login.html';
}

// Minimal client-side state persisted in localStorage
const State = {
  key: 'nutri_state',
  defaults: { calorieGoal: 2000, meals: [], water: 5, bmi: 22.5 },
  init() {
    try {
      const raw = localStorage.getItem(this.key);
      if (raw) {
        const parsed = JSON.parse(raw);
        return Object.assign({}, this.defaults, parsed);
      }
    } catch (e) { console.warn('State.init parse error', e); }
    // save defaults and return a fresh copy
    this.set(Object.assign({}, this.defaults));
    return Object.assign({}, this.defaults);
  },
  get() {
    try {
      const raw = localStorage.getItem(this.key);
      if (raw) {
        return JSON.parse(raw);
      }
    } catch (e) { console.warn('State.get parse error', e); }
    return Object.assign({}, this.defaults);
  },
  set(state) {
    try { localStorage.setItem(this.key, JSON.stringify(state)); } catch (e) { console.warn('State.set error', e); }
  }
};

// Sidebar icons map
const NAV_ICONS = {
  dashboard: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>`,
  meals:     `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M4 3v18M8 3v8a2 2 0 0 1-4 0V3M16 3c-2 0-4 2-4 5s2 5 4 5v8M20 3v18"/></svg>`,
  water:     `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M12 2s-7 8-7 13a7 7 0 0 0 14 0c0-5-7-13-7-13z"/></svg>`,
  bmi:       `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M3 12h4l3-9 4 18 3-9h4"/></svg>`,
  progress:  `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><polyline points="3 17 9 11 13 15 21 7"/><polyline points="14 7 21 7 21 14"/></svg>`,
  assistant: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>`,
  logout:    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>`,
  logo:      `<svg viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" width="26" height="26"><path d="M12 2s-7 8-7 13a7 7 0 0 0 14 0c0-5-7-13-7-13z"/></svg>`
};

function mountSidebar(active = 'dashboard') {
  const mount = document.getElementById('sidebar-mount');
  if (!mount) return;

  const items = [
    { id: 'dashboard', href: 'index.html', key: 'dashboard' },
    { id: 'meals',     href: 'meals.html', key: 'meals' },
    { id: 'water',     href: 'water.html', key: 'water' },
    { id: 'bmi',       href: 'bmi.html',  key: 'bmi' },
    { id: 'progress',  href: 'progress.html', key: 'progress' },
    { id: 'assistant', href: 'chat.html', key: 'assistant' }
  ];

  const navLinks = items.map(it => `
    <a href="${it.href}" class="${it.id === active ? 'active' : ''}" data-i18n="${it.key}">
      ${NAV_ICONS[it.id]}
      <span>${i18n.t(it.key)}</span>
    </a>`).join('');

  const langOptions = ['en','hi','kn','te','ta'].map(l =>
    `<option value="${l}" ${i18n.lang === l ? 'selected' : ''}>${
      {en:'English',hi:'हिन्दी',kn:'ಕನ್ನಡ',te:'తెలుగు',ta:'தமிழ்'}[l]
    }</option>`
  ).join('');

  mount.innerHTML = `
    <aside class="sidebar">
      <div class="logo">
        ${NAV_ICONS.logo}
        <span data-i18n="logo">${i18n.t('logo')}</span>
      </div>
      <nav class="nav">${navLinks}</nav>
      <div class="sidebar-lang">
        <select onchange="i18n.set(this.value);mountSidebar('${active}');">${langOptions}</select>
      </div>
      <div class="sidebar-mode" style="padding:10px; text-align:center;">
        <button id="themeToggleBtn" style="padding:8px 10px;border-radius:8px;border:1px solid #e5e7eb;background:#fff;cursor:pointer;display:flex;align-items:center;gap:8px;justify-content:center;" onclick="toggleTheme()" aria-label="Toggle theme">
          <!-- placeholder; will be populated by initTheme/applyTheme -->
        </button>
      </div>
      <a class="logout" href="#" onclick="logout();return false;">
        ${NAV_ICONS.logout}
        <span data-i18n="logout">${i18n.t('logout')}</span>
      </a>
    </aside>`;

  i18n.translate();
}

// expose State and mountSidebar globally
window.State = State;
window.mountSidebar = mountSidebar;

// Expose i18n globally for pages to call
window.i18n = i18n;

// Theme support: persist and toggle
function applyTheme(theme) {
  if (theme === 'dark') document.documentElement.classList.add('dark-mode');
  else document.documentElement.classList.remove('dark-mode');
  localStorage.setItem('theme', theme);
  const btn = document.getElementById('themeToggleBtn');
  if (btn) {
    const sunIcon = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>`;
    const moonIcon = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>`;
    if (theme === 'dark') {
      btn.innerHTML = `${sunIcon}<span style="font-size:13px">Light</span>`;
      btn.setAttribute('title', 'Switch to light mode');
      btn.setAttribute('aria-pressed', 'true');
    } else {
      btn.innerHTML = `${moonIcon}<span style="font-size:13px">Dark</span>`;
      btn.setAttribute('title', 'Switch to dark mode');
      btn.setAttribute('aria-pressed', 'false');
    }
  }
}

function toggleTheme() {
  const cur = localStorage.getItem('theme') || 'light';
  const next = cur === 'dark' ? 'light' : 'dark';
  applyTheme(next);
}

function initTheme() {
  const saved = localStorage.getItem('theme') || 'light';
  applyTheme(saved);
}

// Auto-translate and init theme on load
document.addEventListener('DOMContentLoaded', () => { initTheme(); i18n.translate(); });
