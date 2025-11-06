import base64
import streamlit.components.v1 as components


# Convert audio file to base64 data URL for HTML embedding
def audio_to_url(path: str, mime: str = "audio/wav") -> str:
    with open(path, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode("utf-8")

    return f"data:{mime};base64,{encoded}"


# Render karaoke player
def karaoke_player(data_url: str, lines):
    js_lines = "["

    for line_idx, line in enumerate(lines):
        js_lines += "["

        for word_idx, w in enumerate(line):
            js_lines += (f'{{start:{w["start"]:.2f}, end:{w["end"]:.2f}, text:"{w["text"]}"}}')
            # Add comma between words but not after last one
            if word_idx < len(line) - 1:
                js_lines += ","
        
        js_lines += "]"

        # Add comma between lines but not after last one
        if line_idx < len(lines) - 1:
            js_lines += ","
    
    js_lines += "]"


    html = f"""
    <style>
      .karaoke-container {{
        background: linear-gradient(135deg, #18181b, #0f172a);
        color: white;
        border-radius: 16px;
        padding: 20px;
        font-family: 'Segoe UI', sans-serif;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
      }}

      .karaoke-title {{
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 12px;
        color: #38bdf8;
      }}

      audio {{
        width: 100%;
        margin-bottom: 10px;
      }}

      .lyric-box {{
        background-color: #1e293b;
        border-radius: 12px;
        padding: 16px;
        min-height: 100px;
        line-height: 1.8;
      }}

      .line {{
        font-size: 22px;
        font-weight: 500;
        margin: 4px 0;
        opacity: 0.4;
        transition: opacity 0.4s ease-in-out;
      }}

      .line.active {{
        opacity: 1;
      }}

      .highlight {{
        color: #22d3ee;
        font-weight: 600;
        transition: color 0.2s linear;
      }}
    </style>

    <div class="karaoke-container">
      <div class="karaoke-title">Karaoke Player</div>
      <audio id="audio" src="{data_url}" controls></audio>

      <div id="lyric-box" class="lyric-box">
        <div id="line1" class="line"></div>
        <div id="line2" class="line"></div>
      </div>
    </div>

    <script>
      const audio = document.getElementById("audio");
      const line1 = document.getElementById("line1");
      const line2 = document.getElementById("line2");

      // Each line is an array of word objects
      const lines = {js_lines};

      let currentLineIndex = 0;
      let currentWordIndex = 0;

      // Render text for one line with highlight on active word
      function renderLine(lineWords, activeWordIndex) {{
        return lineWords.map((w, i) => {{
          if (i === activeWordIndex) {{
            return `<span class='highlight'>${{w.text}}</span>`;
          }}
          return w.text;
        }}).join(" ");
      }}

      // Determine which line and word are active at the given time
      function findActive(t) {{
        for (let i = 0; i < lines.length; i++) {{
          for (let j = 0; j < lines[i].length; j++) {{
            const w = lines[i][j];
            if (t >= w.start && t < w.end) {{
              return [i, j];
            }}
          }}
        }}
        return [0, -1];
      }}

      // Update karaoke text
      function updateDisplay(lineIdx, wordIdx) {{
        const currentLine = lines[lineIdx] || [];
        const nextLine = lines[lineIdx + 1] || [];

        line1.innerHTML = renderLine(currentLine, wordIdx);
        line2.innerHTML = renderLine(nextLine, -1);
        line1.classList.add("active");
        line2.classList.add("active");
      }}

      // Called on every frame
      function tick() {{
        const t = audio.currentTime || 0;
        const [li, wi] = findActive(t);
        if (li !== currentLineIndex || wi !== currentWordIndex) {{
          currentLineIndex = li;
          currentWordIndex = wi;
          updateDisplay(currentLineIndex, currentWordIndex);
        }}
        requestAnimationFrame(tick);
      }}

      // When user seeks (drags progress bar), update instantly
      audio.addEventListener("seeked", () => {{
        const t = audio.currentTime || 0;
        const [li, wi] = findActive(t);
        currentLineIndex = li;
        currentWordIndex = wi;
        updateDisplay(currentLineIndex, currentWordIndex);
      }});

      requestAnimationFrame(tick);
    </script>
    """

    # Render in Streamlit
    components.html(html, height=400, scrolling=False)