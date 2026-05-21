# Quick Start Guide

## Prerequisites
- Python 3.9+
- Node.js 16+
- npm/yarn

## Step-by-Step Setup

### 1. Backend Setup (Terminal 1)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# The .env file already has GROQ_API_KEY configured
# If needed, update it with your own Groq API key from https://console.groq.com

# Start the backend server
python main.py
```

Backend will run at: **http://localhost:8000**

### 2. Frontend Setup (Terminal 2)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run at: **http://localhost:3000**

### 3. Access the Application

Open your browser and go to: **http://localhost:3000**

## Testing the AI Features

### Test 1: Log Interaction

In the AI Assistant chat box (right panel), type:

```
Today I met with Dr. Smith and discussed product X efficiency. The sentiment was positive and I shared the brochures.
```

Expected result:
- Form on left automatically fills with:
  - HCP Name: "Dr. Smith"
  - Topics: "product X efficiency"
  - Sentiment: "Positive"
  - Materials: "brochures"

### Test 2: Edit Interaction

After the form is filled, type:

```
Sorry, the name was actually Dr. John and the sentiment was negative.
```

Expected result:
- HCP Name changes to "Dr. John"
- Sentiment changes to "Negative"
- Other fields remain unchanged

### Test 3: Get Suggestions

After interaction is logged:

```
What should I do next?
```

The AI will generate follow-up suggestions automatically.

### Test 4: Entity Extraction

Type:

```
I met with Dr. Sarah at XYZ Hospital about our new cardiovascular product on March 15, 2024.
```

The system will extract:
- Person: Dr. Sarah
- Organization: XYZ Hospital
- Product: cardiovascular product
- Date: March 15, 2024

## Troubleshooting

### Backend won't start
- Ensure Python 3.9+ is installed: `python --version`
- Check Groq API key is valid in `.env`
- Try: `pip install --upgrade -r requirements.txt`

### Frontend won't connect to backend
- Ensure backend is running on port 8000
- Check VITE_API_URL in `frontend/.env`
- Try hard refresh: `Ctrl+Shift+R`

### Port conflicts
- Backend port 8000: Kill process or change in `main.py`
- Frontend port 3000: Kill process or change in `vite.config.ts`

### Dependencies issues
- Backend: Delete `venv` folder and reinstall
- Frontend: Delete `node_modules` and run `npm install` again

## API Endpoints Available

```
GET  /health                           - Health check
GET  /api/config                       - API configuration
GET  /api/interactions                 - List all interactions
POST /api/interactions                 - Create interaction
GET  /api/interactions/{id}            - Get specific interaction
PUT  /api/interactions/{id}            - Update interaction
DELETE /api/interactions/{id}          - Delete interaction
POST /api/chat                         - Send AI message
GET  /api/conversation-history/{id}    - Get chat history
GET  /api/tools/list                   - List available tools
POST /api/tools/execute                - Execute specific tool
```

## Test Data

You can use these prompts to test the system:

1. **Simple Meeting**: "Met Dr. Johnson, discussed diabetes product, sentiment positive"
2. **Complex Interaction**: "Yesterday at 2 PM, met with Dr. Sarah Chen at Metro Medical Center. Discussed our new cancer treatment protocol. She seemed interested but had some concerns. Positive overall. Shared presentation and samples."
3. **Edit Request**: "Actually, I think the sentiment was more neutral than positive"
4. **Multiple Actions**: "What meetings should I schedule? Who should I follow up with?"

## Production Build

To build for production:

```bash
# Backend - already production ready

# Frontend
cd frontend
npm run build

# Deploy dist/ folder to hosting (Vercel, Netlify, etc.)
```

## Next Steps

1. ✅ Backend running
2. ✅ Frontend running
3. ✅ Test all 5 AI tools
4. ✅ Create interactions via AI
5. ✅ Edit interactions via AI
6. ✅ Generate follow-up suggestions
7. ✅ Extract entities from text
8. ✅ Validate sentiment

## Support

For issues or questions:
- Check Groq API key validity
- Ensure both servers are running
- Check browser console for errors (F12)
- Check terminal output for API errors

---

**Ready to go!** Your AI CRM HCP Module is now set up and ready to use. 🚀
