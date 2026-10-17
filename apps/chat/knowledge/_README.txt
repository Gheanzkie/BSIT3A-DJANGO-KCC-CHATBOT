HOW TO TRAIN KNIGHT
===================

Everything KNIGHT knows comes from the .txt files in this folder. No database.

TO ADD KNOWLEDGE (you do the training):
1. Create a new .txt file in this folder.
2. The FIRST line of the file is the TITLE.
3. The remaining lines are the CONTENT — this is what KNIGHT will answer.
4. Just save it — automatic, no command and no restart needed.
   The next question will already include it.

FROM CHAT (staff/admin account):
- Type: remember: <info>   (or tandaan: <info>)
- New KCC facts found in chat are also saved here automatically (AI_AUTO_LEARN).

NOTES:
- Sub-folders work as category labels (e.g., knowledge/offices/hours.txt).
- Files starting with "_" are ignored by the loader (like this README).
- _embeddings.json is an auto-generated search cache. Safe to delete —
  it rebuilds itself on the next question. Do NOT edit it.
- Simple canned replies (greetings, thanks, goodbye) live in apps/chat/replies.txt.
