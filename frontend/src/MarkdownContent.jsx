import React from "react";

function renderInline(text) {
  const parts = [];
  let remaining = text;
  let key = 0;

  const pattern =
    /(`[^`]+`|\*\*[^*]+\*\*)/;

  while (remaining.length > 0) {
    const match = remaining.match(pattern);

    if (!match) {
      parts.push(
        <span key={key++}>
          {remaining}
        </span>
      );
      break;
    }

    const index = match.index;

    if (index > 0) {
      parts.push(
        <span key={key++}>
          {remaining.slice(0, index)}
        </span>
      );
    }

    const token = match[0];

    if (
      token.startsWith("`") &&
      token.endsWith("`")
    ) {
      parts.push(
        <code
          key={key++}
          className="markdown-inline-code"
        >
          {token.slice(1, -1)}
        </code>
      );
    } else if (
      token.startsWith("**") &&
      token.endsWith("**")
    ) {
      parts.push(
        <strong key={key++}>
          {token.slice(2, -2)}
        </strong>
      );
    }

    remaining =
      remaining.slice(
        index + token.length
      );
  }

  return parts;
}

export default function MarkdownContent({
  content,
}) {
  if (!content) {
    return null;
  }

  const lines =
    content.replace(/\r\n/g, "\n").split("\n");

  const elements = [];
  let paragraph = [];
  let listItems = [];
  let codeLines = [];
  let inCodeBlock = false;
  let codeLanguage = "";
  let key = 0;

  function flushParagraph() {
    if (paragraph.length === 0) {
      return;
    }

    elements.push(
      <p key={key++}>
        {renderInline(
          paragraph.join(" ")
        )}
      </p>
    );

    paragraph = [];
  }

  function flushList() {
    if (listItems.length === 0) {
      return;
    }

    elements.push(
      <ul key={key++}>
        {listItems.map(
          (item, index) => (
            <li key={index}>
              {renderInline(item)}
            </li>
          )
        )}
      </ul>
    );

    listItems = [];
  }

  function flushCode() {
    if (codeLines.length === 0) {
      return;
    }

    elements.push(
      <pre
        key={key++}
        className="markdown-code-block"
      >
        <code>
          {codeLines.join("\n")}
        </code>
      </pre>
    );

    codeLines = [];
    codeLanguage = "";
  }

  for (
    let index = 0;
    index < lines.length;
    index++
  ) {
    const line = lines[index];

    /*
     * CODE BLOCK
     */
    if (line.trim().startsWith("```")) {
      if (!inCodeBlock) {
        flushParagraph();
        flushList();

        inCodeBlock = true;
        codeLanguage =
          line.trim().slice(3).trim();
      } else {
        inCodeBlock = false;
        flushCode();
      }

      continue;
    }

    if (inCodeBlock) {
      codeLines.push(line);
      continue;
    }

    /*
     * BLANK LINE
     */
    if (!line.trim()) {
      flushParagraph();
      flushList();
      continue;
    }

    /*
     * HEADINGS
     */
    if (line.startsWith("### ")) {
      flushParagraph();
      flushList();

      elements.push(
        <h4 key={key++}>
          {renderInline(
            line.slice(4)
          )}
        </h4>
      );

      continue;
    }

    if (line.startsWith("## ")) {
      flushParagraph();
      flushList();

      elements.push(
        <h3 key={key++}>
          {renderInline(
            line.slice(3)
          )}
        </h3>
      );

      continue;
    }

    if (line.startsWith("# ")) {
      flushParagraph();
      flushList();

      elements.push(
        <h2 key={key++}>
          {renderInline(
            line.slice(2)
          )}
        </h2>
      );

      continue;
    }

    /*
     * BULLET LIST
     */
    const bulletMatch =
      line.match(/^\s*[-*]\s+(.*)$/);

    if (bulletMatch) {
      flushParagraph();

      listItems.push(
        bulletMatch[1]
      );

      continue;
    }

    /*
     * NUMBERED LIST
     */
    const numberedMatch =
      line.match(/^\s*\d+\.\s+(.*)$/);

    if (numberedMatch) {
      flushParagraph();

      if (
        listItems.length === 0
      ) {
        listItems = [];
      }

      listItems.push(
        numberedMatch[1]
      );

      continue;
    }

    /*
     * NORMAL TEXT
     */
    flushList();

    paragraph.push(
      line.trim()
    );
  }

  if (inCodeBlock) {
    flushCode();
  }

  flushParagraph();
  flushList();

  return (
    <div className="markdown-content">
      {elements}
    </div>
  );
}