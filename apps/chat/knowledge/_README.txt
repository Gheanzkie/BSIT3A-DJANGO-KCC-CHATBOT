HOW TO TRAIN KNIGHT
===================

Everything KNIGHT knows comes from the .txt files in this folder. No database.

FOLDER MAP (keep new files in the matching folder - the folder name is the
category label KNIGHT sees, so a tidy tree = faster, more accurate answers):

  knowledge/
    kcc/
      about/        school profile, vision-mission, core values, pillars, seal,
                    meaning of KCC, alma mater hymn, contacts
      history/      foundation, fire, presidents, timeline
      academics/    colleges & departments, programs (CEAS/CMAT/Criminology),
                    senior high, basic education
      admissions/   admissions process, tuition & fees per level
      campus-life/  events, sports, outreach, masses, new buildings
      news/         dated school news / announcements summaries
      notes/        facts added from chat ("remember:" / auto-learn)
      handbook/     the official student handbook (121 sections)
    announcements/  auto-generated from published announcements (do not edit)

RULES:
1. Create a new .txt file inside the right topic folder.
2. The FIRST line of the file is the TITLE - make it a plain-language question
   or topic ("How much is BSIT tuition?") so keyword search matches.
3. The remaining lines are the CONTENT - this is what KNIGHT will answer.
4. Save it. No command, no restart. The next question already includes it.
5. Keep one topic per file. Small focused files rank better than one huge file.

FROM CHAT (staff/admin account):
- Type: remember: <info>   (or tandaan: <info>)
- Saved automatically to knowledge/kcc/notes/.
- New KCC facts from staff chat are also auto-saved there (AI_AUTO_LEARN).

NOTES:
- The loader walks every sub-folder recursively; the relative folder path
  becomes the item's category (e.g. "kcc/admissions").
- Files or folders starting with "_" or "." are ignored (like this README).
- _embeddings.json is an auto-generated search cache. Safe to delete - it
  rebuilds itself on the next question. Do NOT edit it.
- Simple canned replies (greetings, thanks, goodbye) live in apps/chat/replies.txt.
