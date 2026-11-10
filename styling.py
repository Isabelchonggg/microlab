"""MicroLab presentation: four pen colours with small pink decorative details."""
CSS = '''<style>
html, body, [data-testid="stApp"], input, textarea, button,
[data-testid="stMarkdownContainer"], [data-baseweb="select"], h1,h2,h3,h4 {
 font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;color:#171717;
}
[data-testid="stAppViewContainer"], [data-testid="stHeader"] {background:#FFF9FB;}
.block-container {max-width:1500px;padding-top:3.2rem;}
.brand {margin:0 0 1rem;}.brand-title {font-size:2.4rem;font-weight:800;letter-spacing:-1px;color:#171717;line-height:1.1;}
.brand-sub {font-size:1.05rem;font-style:italic;color:#C1437F;}
.colour-legend {display:flex;flex-wrap:wrap;gap:.4rem 1rem;background:white;border:1px solid #EEE4E8;
 border-radius:16px;padding:.55rem .8rem;width:fit-content;max-width:100%;box-sizing:border-box;margin:.6rem 0 1.2rem;}
.colour-legend span{display:inline-flex;align-items:center;gap:.35rem;color:#171717;font-size:.86rem;}
.colour-legend i{width:.85rem;height:.85rem;border-radius:50%;display:inline-block;}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:18px;background:#FFFFFF;box-shadow:0 4px 16px #1717170B;}
.stButton button,.stFormSubmitButton button{border-radius:12px;}
.stButton button[kind="primary"],.stFormSubmitButton button[kind="primary"]{background:#171717;color:white;border-color:#171717;}
[data-testid="stExpander"],[data-testid="stForm"]{background:white;border-radius:16px;}
[class*="st-key-math_black_"]{background:#FAFAFA!important;border-color:#171717!important;}
[class*="st-key-math_red_"]{background:#FFF1F1!important;border-color:#DC2626!important;}
[class*="st-key-math_blue_"]{background:#EEF4FF!important;border-color:#2563EB!important;}
[class*="st-key-math_green_"]{background:#EEF9F1!important;border-color:#16803D!important;}
[class*="st-key-math_intuition_"]{background:#FAFAFA!important;border-color:#171717!important;}
[data-testid="stLatex"],.katex-display{max-width:100%;overflow-x:auto;overflow-y:hidden;padding:.2rem 0;}
.mascot{position:fixed;bottom:16px;right:18px;z-index:50;pointer-events:none;width:58px;}
@media(max-width:700px){.mascot{display:none}.brand-title{font-size:2rem}.block-container{padding-top:2.4rem;}[data-testid="stLatex"]{font-size:.86rem;}}
</style>'''
MASCOT = '''<div class="mascot" role="img" aria-label="A little bunny study companion">
<svg viewBox="0 0 100 110" xmlns="http://www.w3.org/2000/svg">
<ellipse cx="34" cy="25" rx="12" ry="23" fill="white" stroke="#C1437F" stroke-width="2"/>
<ellipse cx="66" cy="25" rx="12" ry="23" fill="white" stroke="#C1437F" stroke-width="2"/>
<ellipse cx="34" cy="24" rx="5" ry="15" fill="#FFD6E8"/><ellipse cx="66" cy="24" rx="5" ry="15" fill="#FFD6E8"/>
<ellipse cx="50" cy="61" rx="40" ry="33" fill="white" stroke="#C1437F" stroke-width="2"/>
<circle cx="36" cy="57" r="3" fill="#171717"/><circle cx="64" cy="57" r="3" fill="#171717"/>
<path d="M45 68 Q50 75 55 68" fill="none" stroke="#171717" stroke-width="2"/>
<path d="M22 82 Q36 77 50 85 Q64 77 78 82 L78 103 Q64 98 50 106 Q36 98 22 103Z" fill="#FFD6E8" stroke="#C1437F" stroke-width="2"/>
</svg></div>'''
