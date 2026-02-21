"""
Eye Diseases Information Database
Comprehensive information about various eye conditions
"""

EYE_DISEASES = {
    "Cataract": {
        "description": "Cataracts are a common eye condition causing cloudiness in the lens, leading to blurred vision.",
        "icon": "☁️",
        "severity": "Common",
        "treated": "Over 20 lakh+ eyes treated"
    },
    "Glaucoma": {
        "description": "Glaucoma is a stealthy sight-stealer, a disease that sneaks up on your eyes, stealing your sight slowly.",
        "icon": "👁️",
        "severity": "Serious",
        "treated": "Requires ongoing monitoring"
    },
    "Diabetic Retinopathy": {
        "description": "Diabetic Retinopathy is a condition where diabetes can harm your eyes over time. If unchecked, can lead to vision problems.",
        "icon": "🩸",
        "severity": "Progressive",
        "treated": "Early detection crucial"
    },
    "Corneal Ulcer (Keratitis)": {
        "description": "A corneal ulcer (keratitis) is an erosion or an open sore on the cornea that can cause pain and vision problems.",
        "icon": "🔴",
        "severity": "Urgent",
        "treated": "Requires immediate attention"
    },
    "Fungal Keratitis": {
        "description": "Fungal infection of the cornea that can cause severe inflammation and vision loss if not treated promptly.",
        "icon": "🦠",
        "severity": "Serious",
        "treated": "Specialized treatment needed"
    },
    "Macular Hole": {
        "description": "A macular hole is a small break or defect in the macula, affecting central vision.",
        "icon": "⭕",
        "severity": "Moderate",
        "treated": "Surgical repair available"
    },
    "Retinopathy of Prematurity": {
        "description": "Retinopathy of Prematurity (ROP) is an eye condition that affects premature babies, causing abnormal blood vessel growth.",
        "icon": "👶",
        "severity": "Pediatric",
        "treated": "Early screening essential"
    },
    "Retinal Detachment": {
        "description": "Retinal detachment is a serious eye condition in which the retina separates from the back of the eye.",
        "icon": "⚠️",
        "severity": "Emergency",
        "treated": "Immediate surgery required"
    },
    "Keratoconus": {
        "description": "Keratoconus is a progressive eye condition that causes the cornea to thin and bulge into a cone shape.",
        "icon": "🔺",
        "severity": "Progressive",
        "treated": "Corneal strengthening available"
    },
    "Macular Edema": {
        "description": "The macula swells due to fluid buildup, affecting central vision and clarity.",
        "icon": "💧",
        "severity": "Moderate",
        "treated": "Multiple treatment options"
    },
    "Squint (Strabismus)": {
        "description": "Squint, or strabismus, is when the eyes don't align properly, causing one or both to turn in different directions.",
        "icon": "👀",
        "severity": "Common",
        "treated": "Correctable with treatment"
    },
    "Uveitis": {
        "description": "Uveitis is a hidden threat to your eyes, a condition characterised by inflammation that can quietly affect your vision.",
        "icon": "🔥",
        "severity": "Serious",
        "treated": "Anti-inflammatory treatment"
    },
    "Pterygium (Surfer's Eye)": {
        "description": "Pterygium, commonly known as Surfer's Eye, is a non-cancerous growth on the eye's surface.",
        "icon": "🌊",
        "severity": "Mild",
        "treated": "Surgical removal if needed"
    },
    "Blepharitis": {
        "description": "Blepharitis is a common and chronic condition that causes inflammation of the eyelids.",
        "icon": "👁️‍🗨️",
        "severity": "Chronic",
        "treated": "Manageable with hygiene"
    },
    "Nystagmus": {
        "description": "Nystagmus is a neurological eye condition that causes involuntary, repetitive eye movements.",
        "icon": "↔️",
        "severity": "Neurological",
        "treated": "Specialized care needed"
    },
    "Ptosis (Droopy Eyelid)": {
        "description": "Ptosis, commonly known as droopy eyelid, occurs when the upper eyelid droops over the eye.",
        "icon": "😴",
        "severity": "Cosmetic/Functional",
        "treated": "Surgical correction available"
    },
    "Conjunctivitis (Pink Eye)": {
        "description": "Inflammation of conjunctiva (transparent membrane covering white part of the eye), often causing redness and discharge.",
        "icon": "🔴",
        "severity": "Common",
        "treated": "Usually self-limiting"
    },
    "Behcet's Disease": {
        "description": "Behcet's Disease, also called Silk Road Disease, is an autoimmune disease affecting multiple organs including eyes.",
        "icon": "🛡️",
        "severity": "Autoimmune",
        "treated": "Immunosuppressive therapy"
    },
    "Computer Vision Syndrome": {
        "description": "Computer Vision Syndrome (CVS), also known as digital eye strain, results from prolonged screen use.",
        "icon": "💻",
        "severity": "Modern Epidemic",
        "treated": "Preventable with breaks"
    },
    "Hypertensive Retinopathy": {
        "description": "Damage to the retina and retinal circulation caused by high blood pressure.",
        "icon": "📈",
        "severity": "Progressive",
        "treated": "Blood pressure control"
    },
    "Mucormycosis (Black Fungus)": {
        "description": "Black fungus, scientifically known as mucormycosis, is a rare but serious fungal infection.",
        "icon": "⚫",
        "severity": "Life-threatening",
        "treated": "Emergency treatment"
    },
    "Eye Twitching (Myokymia)": {
        "description": "An eye twitch, medically known as myokymia, is a repetitive, involuntary spasm of the eyelid.",
        "icon": "😖",
        "severity": "Benign",
        "treated": "Usually self-resolving"
    },
    "Myopia (Nearsightedness)": {
        "description": "Myopia, commonly known as nearsightedness, is a vision condition where distant objects appear blurry.",
        "icon": "🔍",
        "severity": "Very Common",
        "treated": "Correctable with glasses/surgery"
    },
    "Stye": {
        "description": "A stye is a painful, swollen bump that forms on the edge of the eyelid, caused by bacterial infection.",
        "icon": "🔴",
        "severity": "Minor",
        "treated": "Warm compresses help"
    },
    "Central Serous Retinopathy": {
        "description": "Fluid buildup under the retina causing blurred or distorted central vision.",
        "icon": "💧",
        "severity": "Moderate",
        "treated": "Often self-resolving"
    },
    "Hyperopia (Farsightedness)": {
        "description": "Hyperopia is a vision condition where nearby objects appear blurry while distant objects are clear.",
        "icon": "👓",
        "severity": "Common",
        "treated": "Correctable with glasses/surgery"
    }
}

DISEASE_CATEGORIES = {
    "Emergency Conditions": ["Retinal Detachment", "Mucormycosis (Black Fungus)", "Corneal Ulcer (Keratitis)"],
    "Common Conditions": ["Cataract", "Myopia (Nearsightedness)", "Hyperopia (Farsightedness)", "Conjunctivitis (Pink Eye)", "Computer Vision Syndrome"],
    "Retinal Diseases": ["Diabetic Retinopathy", "Hypertensive Retinopathy", "Retinopathy of Prematurity", "Macular Edema", "Central Serous Retinopathy"],
    "Corneal Conditions": ["Keratoconus", "Fungal Keratitis", "Pterygium (Surfer's Eye)"],
    "Inflammatory Conditions": ["Uveitis", "Blepharitis", "Behcet's Disease"],
    "Structural Issues": ["Glaucoma", "Macular Hole", "Ptosis (Droopy Eyelid)", "Squint (Strabismus)", "Nystagmus"]
}
