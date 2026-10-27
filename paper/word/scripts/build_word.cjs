#!/usr/bin/env node
// 将整理好的正文及审阅锚点生成可编辑Word；只新建本目录的交付文件。
const fs = require('fs');
const path = require('path');
const moduleRoot = process.env.CODEX_NODE_MODULES || '/Users/easylife/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const d = require(path.join(moduleRoot, 'docx'));
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
  Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType, TableLayoutType,
  VerticalAlign, LineRuleType, PageNumber, Math: OfficeMath, MathRun, MathSubScript,
  InsertedTextRun, DeletedTextRun, CommentRangeStart, CommentRangeEnd, CommentReference,
} = d;
const OUT = path.resolve(__dirname, '..');
const article = JSON.parse(fs.readFileSync(path.join(OUT, 'article.review.json'), 'utf8'));
const refs = JSON.parse(fs.readFileSync(path.join(OUT, 'references.json'), 'utf8'));
const FONT = { ascii: 'Times New Roman', hAnsi: 'Times New Roman', eastAsia: '宋体', cs: 'Times New Roman' };
const BODY = { font: FONT, size: 24, color: '000000' };
const WIDTH = 9026; // A4，四边2.54cm；图表不超出版心。
const WIDTH_PX = WIDTH / 15;
let revisionSequence = 1000;
let renderedRevisions = [];

function textRun(text, options = {}) {
  return new TextRun({ ...BODY, text, ...options });
}

function mathParts(raw) {
  const result = [];
  const pattern = /([A-Za-z])_\{([^}]+)\}|([A-Za-z])_([A-Za-z])/g;
  let cursor = 0, match;
  while ((match = pattern.exec(raw)) !== null) {
    if (match.index > cursor) result.push(new MathRun(raw.slice(cursor, match.index)));
    result.push(new MathSubScript({ children: [new MathRun(match[1] || match[3])],
                                   subScript: [new MathRun(match[2] || match[4])] }));
    cursor = pattern.lastIndex;
  }
  if (cursor < raw.length) result.push(new MathRun(raw.slice(cursor)));
  return result;
}

function plainRuns(text, options = {}) {
  // 数学保持为Word原生公式，不将LaTeX转义符排进正文。
  const result = [];
  const pattern = /\\\((.*?)\\\)/g;
  let cursor = 0, match;
  while ((match = pattern.exec(text)) !== null) {
    if (match.index > cursor) result.push(textRun(text.slice(cursor, match.index), options));
    result.push(new OfficeMath({ children: mathParts(match[1]) }));
    cursor = pattern.lastIndex;
  }
  if (cursor < text.length) result.push(textRun(text.slice(cursor), options));
  return result.length ? result : [textRun('', options)];
}

function richRuns(block, review, options = {}) {
  const text = block.text || '';
  if (!review) return plainRuns(text, options);
  const spans = block.revisions || [];
  const comments = block.comments || [];
  const deletions = block.deletions || [];
  const cuts = new Set([0, text.length]);
  spans.forEach(s => { cuts.add(s.start); cuts.add(s.end); });
  comments.forEach(c => { cuts.add(c.start); cuts.add(c.end); });
  deletions.forEach(s => cuts.add(s.at));
  const positions = [...cuts].filter(x => x >= 0 && x <= text.length).sort((a, b) => a - b);
  const result = [];
  positions.forEach((at, index) => {
    // 先结束前一区间的评论，再开启当前区间的评论，保留跨段评论的标识。
    comments.filter(c => c.end === at && c.start !== c.end).forEach(c => {
      result.push(new CommentRangeEnd(c.id));
      result.push(new TextRun({ ...BODY, children: [new CommentReference(c.id)] }));
    });
    comments.filter(c => c.start === at).forEach(c => result.push(new CommentRangeStart(c.id)));
    deletions.filter(s => s.at === at).forEach(s => {
      const id = revisionSequence++;
      renderedRevisions.push({ word_id: id, group_id: s.id, type: 'delete', author: s.author,
        date: s.date, source: s.source, source_revision_id: s.source_revision_id });
      result.push(new DeletedTextRun({ ...BODY, ...options, id, author: s.author, date: s.date, text: s.text }));
    });
    comments.filter(c => c.end === at && c.start === c.end).forEach(c => {
      result.push(new CommentRangeEnd(c.id));
      result.push(new TextRun({ ...BODY, children: [new CommentReference(c.id)] }));
    });
    if (index === positions.length - 1) return;
    const end = positions[index + 1];
    if (at === end) return;
    const rev = spans.find(s => s.start <= at && s.end >= end);
    if (rev) {
      const id = revisionSequence++;
      renderedRevisions.push({ word_id: id, group_id: rev.id, type: 'insert', author: rev.author,
        date: rev.date, source: rev.source, source_revision_id: rev.source_revision_id });
      result.push(new InsertedTextRun({ ...BODY, ...options, id,
        author: rev.author, date: rev.date, text: text.slice(at, end).replace(/\\\((.*?)\\\)/g, '$1') }));
    }
    else result.push(...plainRuns(text.slice(at, end), options));
  });
  return result;
}

function paragraph(block, review, properties = {}, runOptions = {}) {
  return new Paragraph({ style: 'Normal', children: richRuns(block, review, runOptions), ...properties });
}

function makeTable(block) {
  const cols = [950, 4776, 3300];
  const no = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
  const rule = { style: BorderStyle.SINGLE, size: 8, color: '000000' };
  const rows = [block.headers, ...block.rows].map((row, index, all) => new TableRow({
    tableHeader: index === 0,
    cantSplit: true,
    children: row.map((value, column) => new TableCell({
      width: { size: cols[column], type: WidthType.DXA },
      verticalAlign: VerticalAlign.CENTER,
      margins: { top: 90, bottom: 90, left: 95, right: 95 },
      borders: { left: no, right: no,
                 top: index === 0 ? rule : no,
                 bottom: index === 0 || index === all.length - 1 ? rule : no },
      children: [new Paragraph({
        children: plainRuns(String(value), { size: 21, bold: index === 0 }),
        alignment: column === 0 ? AlignmentType.CENTER : AlignmentType.LEFT,
        spacing: { line: 300, lineRule: LineRuleType.EXACT, before: 0, after: 0 },
        indent: { firstLine: 0 },
      })],
    })),
  }));
  return new Table({ width: { size: WIDTH, type: WidthType.DXA },
                     columnWidths: cols, layout: TableLayoutType.FIXED,
                     borders: { top: no, bottom: no, left: no, right: no, insideHorizontal: no, insideVertical: no },
                     rows, alignment: AlignmentType.CENTER });
}

function imageSize(buffer) {
  // 本次五图均为PNG，直接读取IHDR保证按原始比例缩放。
  return [buffer.readUInt32BE(16), buffer.readUInt32BE(20)];
}

function makeComments() {
  return (article.comments || []).map(c => ({
    id: c.id, author: c.author || '原稿批注', initials: c.initials || '',
    date: new Date(c.date || '2026-10-18T00:00:00Z'),
    children: String(c.text).split('\n').map(line => new Paragraph({
      children: plainRuns(line, { size: 21 }),
      spacing: { line: 280, lineRule: LineRuleType.AUTO, after: 80 },
      indent: { firstLine: 0 },
    })),
  }));
}

function deletedParagraphs(change) {
  return String(change.source_text || '').split(/\n\s*\n/).filter(s => s.trim()).map(raw => {
    const value = raw.replace(/\*\*/g, '').replace(/\n/g, ' ').replace(/^>\s*/, '');
    const id = revisionSequence++;
    renderedRevisions.push({ word_id: id, type: 'delete', author: 'Claude', date: '2026-10-18T00:00:00Z',
      editorial_change_id: change.id, reason: change.reason });
    return new Paragraph({ style: 'LegacyDeletion', spacing: { before: 0, after: 0 },
      children: [new DeletedTextRun({ ...BODY, id, text: value, author: 'Claude', date: '2026-10-18T00:00:00Z' })] });
  });
}

function build(review) {
  const children = [];
  const finalParagraphs = article.blocks.filter(b => b.kind === 'paragraph');
  const penultimate = finalParagraphs.at(-2)?.id;
  const last = finalParagraphs.at(-1)?.id;
  const titleBreak = article.title.indexOf('：');
  const titleRuns = titleBreak >= 0
    ? [textRun(article.title.slice(0, titleBreak + 1), { bold: true, size: 36 }),
       textRun(article.title.slice(titleBreak + 1), { bold: true, size: 32, break: 1 })]
    : [textRun(article.title, { bold: true, size: 36 })];
  children.push(new Paragraph({
    style: 'Title', alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 240, line: 460, lineRule: LineRuleType.EXACT },
    children: titleRuns,
  }));
  for (const block of article.blocks) {
    if (review && block.kind === 'heading1' && block.text.startsWith('三、')) {
      for (const change of article.changes.filter(c => c.action === 'omit_superseded_sections')) {
        children.push(...deletedParagraphs(change));
      }
    }
    switch (block.kind) {
      case 'abstract':
        children.push(new Paragraph({ style: 'Normal', indent: { firstLine: 0 },
          spacing: { after: 120, before: 0, line: 400, lineRule: LineRuleType.EXACT },
          children: [textRun('摘要：', { bold: true }), ...richRuns(block, review)] }));
        break;
      case 'keywords':
        children.push(new Paragraph({ style: 'Normal', indent: { firstLine: 0 }, spacing: { after: 240 },
          children: [textRun('关键词：', { bold: true }), ...richRuns(block, review)] }));
        break;
      case 'heading1':
        children.push(paragraph(block, review, {
          style: 'Heading1', keepNext: true, keepLines: true, indent: { firstLine: 0 },
          spacing: { before: 240, after: 100, line: 400, lineRule: LineRuleType.EXACT } },
          { bold: true, size: 28 }));
        break;
      case 'heading2':
        children.push(paragraph(block, review, {
          style: 'Heading2', keepNext: true, keepLines: true, indent: { firstLine: 0 },
          spacing: { before: 160, after: 80, line: 400, lineRule: LineRuleType.EXACT } },
          { bold: true, size: 24 }));
        break;
      case 'research_question':
        children.push(new Paragraph({ style: 'Normal', children: [textRun(`${block.number}. `), ...richRuns(block, review)],
          indent: { left: 480, hanging: 360 }, spacing: { before: 0, after: 80 } }));
        break;
      case 'equation':
        children.push(new Paragraph({ alignment: AlignmentType.CENTER, indent: { firstLine: 0 },
          spacing: { before: 160, after: 160, line: 460, lineRule: LineRuleType.EXACT },
          children: [new OfficeMath({ children: mathParts(block.text) })] }));
        break;
      case 'figure': {
        const imagePath = path.resolve(OUT, block.path);
        const buffer = fs.readFileSync(imagePath);
        const [w, h] = imageSize(buffer);
        children.push(new Paragraph({ alignment: AlignmentType.CENTER, indent: { firstLine: 0 },
          keepNext: true, spacing: { before: 140, after: 80, line: 240, lineRule: LineRuleType.AUTO },
          children: [new ImageRun({ type: 'png', data: buffer,
            transformation: { width: WIDTH_PX, height: WIDTH_PX * h / w },
            altText: { title: `图${block.number} ${block.title}`, description: block.caption, name: `Figure ${block.number}` },
          })] }));
        children.push(new Paragraph({ alignment: AlignmentType.CENTER, indent: { firstLine: 0 },
          keepNext: true, spacing: { before: 0, after: 60, line: 300, lineRule: LineRuleType.EXACT },
          children: plainRuns(`图${block.number}　${block.title}`, { size: 21, bold: true }) }));
        children.push(new Paragraph({ indent: { firstLine: 0 }, alignment: AlignmentType.JUSTIFIED,
          keepLines: true, spacing: { before: 0, after: 140, line: 300, lineRule: LineRuleType.EXACT },
          children: plainRuns(`注：${block.caption.replace(/^注[：:]\s*/, '')}`, { size: 21 }) }));
        break;
      }
      case 'table':
        children.push(new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true,
          indent: { firstLine: 0 }, spacing: { before: 160, after: 80 },
          children: plainRuns(`表${block.number}　${block.title}`, { bold: true, size: 21 }) }));
        children.push(makeTable(block));
        children.push(new Paragraph({ indent: { firstLine: 0 },
          spacing: { before: 70, after: 140, line: 300, lineRule: LineRuleType.EXACT },
          children: plainRuns(`注：${block.note}`, { size: 21 }) }));
        break;
      case 'reference': break; // 统一在文末按APA顺序写入去重后的书目。
      default:
        children.push(paragraph(block, review, { keepNext: block.id === penultimate,
                                                keepLines: block.id === last }));
    }
  }
  if (review) {
    for (const change of article.changes.filter(c => c.action === 'omit_internal_appendix_placeholder')) {
      children.push(...deletedParagraphs(change));
    }
  }
  children.push(new Paragraph({ style: 'Heading1',
    pageBreakBefore: true, keepNext: true, indent: { firstLine: 0 },
    spacing: { before: 0, after: 160 }, children: [textRun('参考文献', { bold: true, size: 28 })] }));
  for (const ref of [...refs].sort((a, b) => a.sortkey.localeCompare(b.sortkey, 'en'))) {
    const runs = (ref.runs || [{ text: ref.text }]).flatMap(r => plainRuns(r.text, {
      italics: !!r.italic && !/[\u3400-\u9fff]/.test(r.text),
    }));
    children.push(new Paragraph({ style: 'Bibliography', children: runs,
      alignment: AlignmentType.LEFT, indent: { left: 480, hanging: 480 },
      spacing: { before: 0, after: 100, line: 360, lineRule: LineRuleType.EXACT },
      keepLines: true,
    }));
  }
  const doc = new Document({
    title: article.title, subject: 'ICA 2027 CAT 中文论文工作稿', creator: '', lastModifiedBy: '',
    description: review ? '完整正文，保留原稿批注和修订。' : '完整正文清洁阅读版。',
    styles: {
      default: { document: { run: BODY,
        paragraph: { alignment: AlignmentType.JUSTIFIED,
          spacing: { before: 0, after: 0, line: 400, lineRule: LineRuleType.EXACT },
          indent: { firstLine: 480 }, widowControl: true } } },
      paragraphStyles: [
        { id: 'Normal', name: 'Normal', run: BODY,
          paragraph: { spacing: { before: 0, after: 0, line: 400, lineRule: LineRuleType.EXACT },
            indent: { firstLine: 480 }, alignment: AlignmentType.JUSTIFIED, widowControl: true } },
        { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
          run: { ...BODY, bold: true, size: 28 }, paragraph: { outlineLevel: 0, keepNext: true, indent: { firstLine: 0 } } },
        { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
          run: { ...BODY, bold: true }, paragraph: { outlineLevel: 1, keepNext: true, indent: { firstLine: 0 } } },
        { id: 'Title', name: 'Title', basedOn: 'Normal', run: { ...BODY, bold: true, size: 36 },
          paragraph: { alignment: AlignmentType.CENTER, indent: { firstLine: 0 } } },
        { id: 'Bibliography', name: 'Bibliography', basedOn: 'Normal', run: BODY,
          paragraph: { indent: { left: 480, hanging: 480 }, alignment: AlignmentType.LEFT } },
        { id: 'LegacyDeletion', name: 'Legacy deletion', basedOn: 'Normal', run: BODY,
          paragraph: { spacing: { before: 0, after: 0 } } },
      ],
    },
    settings: { trackRevisions: review, updateFields: true, defaultTabStop: 480 },
    comments: review ? { children: makeComments() } : undefined,
    sections: [{
      properties: { page: { size: { width: 11906, height: 16838 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440, header: 720, footer: 850 } } },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
        indent: { firstLine: 0 }, spacing: { before: 0, after: 0, line: 240 },
        children: [new TextRun({ font: FONT, size: 18, children: [PageNumber.CURRENT] })] })] }) },
      children,
    }],
  });
  return doc;
}

async function main() {
  for (const review of [true, false]) {
    const name = review ? '悼念退潮之后_完整中文稿_保留批注修订.docx' : '悼念退潮之后_完整中文稿.docx';
    const buffer = await Packer.toBuffer(build(review));
    fs.writeFileSync(path.join(OUT, name), buffer);
    if (review) fs.writeFileSync(path.join(OUT, 'qa/word_revision_mapping.json'), JSON.stringify(renderedRevisions, null, 2));
    console.log(name, buffer.length);
  }
}
main().catch(error => { console.error(error); process.exit(1); });
