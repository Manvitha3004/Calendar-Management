const GEMINI_API_KEY = 'AIzaSyDqPX6uJWY_hoRI958JnAf043W01P2txYc';
const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=' + GEMINI_API_KEY;

/**
 * Sends the meeting description to Gemini API and returns a structured summary.
 * @param {string} description - The raw meeting description text.
 * @returns {Promise<Object>} - The summary object with keys: purpose, background, keyPoints, actionItems, stakeholders.
 */
export async function generatePrepSummary(description) {
  if (!description || description.trim() === '') {
    return {
      purpose: 'No description provided.',
      background: '',
      keyPoints: '',
      actionItems: '',
      stakeholders: '',
    };
  }

  const promptText = `You are a meeting preparation assistant. Summarize the following meeting description into:
- Purpose
- Background
- Key Talking Points
- Action Items
- Stakeholders

Description:
${description}

Expected Output Example:

Purpose: Discuss go-to-market strategy  
Background: Quantum-resistant blockchain product nearing prototype  
Key Points:
- Timeline for technical milestones  
- Marketing rollout plan  
- Target enterprise segments  
Action Items:
- Assign owners to outreach  
- Finalize messaging strategy  
Stakeholders: Anil (Marketing), Riya (Engineering)`;

  const body = {
    contents: [
      {
        parts: [
          {
            text: promptText,
          },
        ],
      },
    ],
  };

  try {
    const response = await fetch(GEMINI_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Gemini API error:', errorText);
      throw new Error('Failed to generate summary from Gemini API');
    }

    const data = await response.json();

    // Extract the generated text from the response
    const generatedText = data?.candidates?.[0]?.content || '';

    if (!generatedText) {
      console.warn('Gemini API returned empty content');
      return {
        purpose: 'No description provided.',
        background: '',
        keyPoints: '',
        actionItems: '',
        stakeholders: '',
      };
    }

    // Parse the generated text into structured fields
    const summary = {
      purpose: '',
      background: '',
      keyPoints: '',
      actionItems: '',
      stakeholders: '',
    };

    const lines = generatedText.split('\n').map(line => line.trim());

    let currentField = null;
    lines.forEach(line => {
      if (line.toLowerCase().startsWith('purpose:')) {
        currentField = 'purpose';
        summary.purpose = line.substring(8).trim();
      } else if (line.toLowerCase().startsWith('background:')) {
        currentField = 'background';
        summary.background = line.substring(11).trim();
      } else if (line.toLowerCase().startsWith('key points:') || line.toLowerCase().startsWith('key talking points:')) {
        currentField = 'keyPoints';
        summary.keyPoints += (summary.keyPoints ? '\n' : '') + line.substring(line.indexOf(':') + 1).trim();
      } else if (line.toLowerCase().startsWith('action items:')) {
        currentField = 'actionItems';
        summary.actionItems += (summary.actionItems ? '\n' : '') + line.substring(13).trim();
      } else if (line.toLowerCase().startsWith('stakeholders:')) {
        currentField = 'stakeholders';
        summary.stakeholders += (summary.stakeholders ? '\n' : '') + line.substring(12).trim();
      } else if (currentField) {
        summary[currentField] += (summary[currentField] ? '\n' : '') + line;
      }
    });

    return summary;
  } catch (error) {
    console.error('Error in generatePrepSummary:', error);
    return {
      purpose: 'No description provided.',
      background: '',
      keyPoints: '',
      actionItems: '',
      stakeholders: '',
    };
  }
}
