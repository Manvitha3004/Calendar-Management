/**
 * Utility function to generate a structured meeting brief summary
 * from a meeting description string.
 * 
 * This is a simple template-based summarization.
 * If an LLM API is available, it can be integrated here for enhanced summaries.
 */

export async function generateMeetingBrief(description) {
  if (!description || description.trim() === '') {
    return {
      purpose: 'No description provided.',
      background: '',
      participants: '',
      outcomes: '',
    };
  }

  // Simple heuristic-based extraction (can be improved or replaced with LLM API)
  // For now, split description into lines and assign to fields based on keywords

  const lines = description.split('\n').map(line => line.trim()).filter(line => line.length > 0);

  let purpose = '';
  let background = '';
  let participants = '';
  let outcomes = '';

  lines.forEach(line => {
    const lower = line.toLowerCase();
    if (lower.includes('purpose') || lower.includes('goal')) {
      purpose += line + ' ';
    } else if (lower.includes('background') || lower.includes('context')) {
      background += line + ' ';
    } else if (lower.includes('participant') || lower.includes('attendee')) {
      participants += line + ' ';
    } else if (lower.includes('outcome') || lower.includes('result')) {
      outcomes += line + ' ';
    }
  });

  // Fallback: if fields are empty, assign first lines accordingly
  if (!purpose) purpose = lines[0] || '';
  if (!background && lines.length > 1) background = lines[1];
  if (!participants && lines.length > 2) participants = lines[2];
  if (!outcomes && lines.length > 3) outcomes = lines[3];

  return {
    purpose: purpose.trim(),
    background: background.trim(),
    participants: participants.trim(),
    outcomes: outcomes.trim(),
  };
}
