name: Daily Spanish Workout

on:
  schedule:
    - cron: '0 8 * * *' # Runs automatically every day at 8:00 AM UTC
  workflow_dispatch: # Allows you to trigger it manually anytime

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    # 1. Download your repository files onto the runner
    - name: Checkout repository
      uses: actions/checkout@v4

    # 2. Set up Python environment
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    # 3. Install dependencies (including the markdown styling translator)
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install google-genai markdown

    # 4. Run your python script to generate today's file
    - name: Run workout generator
      env:
        GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
      run: python generate_workout.py

    # 5. Convert the raw text file into a gorgeously styled HTML layout
    - name: Convert Workout to Beautiful HTML
      run: |
        python -c '
        import markdown
        
        # Read raw workout text
        with open("workout.md", "r", encoding="utf-8") as f:
            text = f.read()
            
        # Convert text formatting to HTML
        html_body = markdown.markdown(text, extensions=["extra", "nl2br"])
        
        # Wrap it in premium email styling (clean fonts, padding, blockquotes)
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    color: #2d3748;
                    line-height: 1.7;
                    background-color: #f7fafc;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: #ffffff;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                    border: 1px solid #e2e8f0;
                }}
                h1, h2, h3 {{
                    color: #1a202c;
                    margin-top: 24px;
                    margin-bottom: 12px;
                }}
                h1 {{ font-size: 24px; color: #2b6cb0; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
                h2 {{ font-size: 20px; color: #2d3748; margin-top: 20px; }}
                p, li {{ font-size: 16px; color: #4a5568; }}
                ul, ol {{ padding-left: 20px; margin-bottom: 16px; }}
                li {{ margin-bottom: 6px; }}
                blockquote {{
                    margin: 16px 0;
                    padding: 12px 16px;
                    color: #2c5282;
                    border-left: 4px solid #3182ce;
                    background-color: #ebf8ff;
                    border-radius: 0 4px 4px 0;
                }}
                strong {{ color: #1a202c; }}
            </style>
        </head>
        <body>
            <div class="container">
                {html_body}
            </div>
        </body>
        </html>
        """
        
        with open("workout.html", "w", encoding="utf-8") as f:
            f.write(full_html)
        '

    # 6. Safely stage, commit, and sync your new markdown file to GitHub
    - name: Commit and push changes
      run: |
        git config --global user.name "github-actions[bot]"
        git config --global user.email "github-actions[bot]@users.noreply.github.com"
        
        git add workout.md
        git commit -m "Update daily workout [skip ci]" || echo "No changes to commit"
        
        git pull --rebase origin main || git pull --rebase origin master || echo "No remote changes to merge"
        git push origin HEAD

    # 7. Send the beautifully formatted HTML email directly to your inbox
    - name: Send Daily Workout Email
      uses: dawidd6/action-send-mail@v4
      with:
        server_address: smtp.gmail.com
        server_port: 465
        username: vmgrosso02@gmail.com
        password: ${{ secrets.EMAIL_PASSWORD }}
        subject: "🏋️‍♂️ Tu Práctica de Español - Daily Workout"
        to: vmgrosso02@gmail.com
        from: "Gemini Spanish Tutor <vmgrosso02@gmail.com>"
        html_body: file://workout.html
