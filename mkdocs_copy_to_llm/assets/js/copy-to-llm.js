// Copy to LLM functionality
// This script adds "Copy to LLM" buttons to code blocks and content sections
(function() {
  'use strict';

  // Helper function to format code for LLM consumption
  function formatCodeForLLM(codeElement, language) {
    const code = codeElement.textContent;
    const context = getPageContext();
    
    return `# Context from Polkadot Documentation
Page: ${context.title}
Section: ${context.section}
URL: ${context.url}

\`\`\`${language}
${code}
\`\`\``;
  }

  // Helper function to format content section for LLM
  function formatSectionForLLM(sectionElement) {
    const context = getPageContext();
    const content = cleanContentForLLM(sectionElement);
    
    return `# Polkadot Documentation Section
Page: ${context.title}
URL: ${context.url}

${content}`;
  }

  // Get current page context
  function getPageContext() {
    return {
      title: document.title,
      section: getCurrentSection(),
      url: window.location.href
    };
  }

  // Get current section heading
  function getCurrentSection() {
    const headings = document.querySelectorAll('h1, h2, h3');
    for (let heading of headings) {
      if (heading.getBoundingClientRect().top > 0) {
        return heading.textContent.trim();
      }
    }
    return 'Main Content';
  }
  
  // Get current section element
  function getCurrentSectionElement() {
    const headings = document.querySelectorAll('.md-content h2, .md-content h3');
    let currentHeading = null;
    
    // Find the current visible section
    for (let heading of headings) {
      const rect = heading.getBoundingClientRect();
      if (rect.top > 100) break; // Stop at first heading below viewport
      if (rect.top <= 100) currentHeading = heading;
    }
    
    if (currentHeading) {
      return getSectionContent(currentHeading);
    }
    
    // Return entire content if no specific section
    return document.querySelector('.md-content__inner .md-typeset');
  }
  
  // Get the raw markdown file URL
  function getMdFileUrl() {
    // Get current page path
    const currentPath = window.location.pathname;
    
    // Remove trailing slash if present
    let path = currentPath.endsWith('/') ? currentPath.slice(0, -1) : currentPath;
    
    // If path is empty or just /, use index
    if (!path || path === '') {
      path = '/index';
    }
    
    // Convert the HTML path to markdown path
    // The raw markdown files are in the root of the repository
    const baseUrl = 'https://raw.githubusercontent.com/polkadot-developers/polkadot-docs/refs/heads/master';
    const mdPath = path + '.md';
    
    return baseUrl + mdPath;
  }
  
  // Remove front matter (metadata) from markdown content
  function removeFrontMatter(content) {
    // Check if content starts with ---
    if (!content.startsWith('---')) {
      return content;
    }
    
    // Find the second --- that closes the front matter
    const lines = content.split('\n');
    let endIndex = -1;
    
    // Start from line 1 (skip the first ---)
    for (let i = 1; i < lines.length; i++) {
      if (lines[i].trim() === '---') {
        endIndex = i;
        break;
      }
    }
    
    // If we found the closing ---, remove everything up to and including it
    if (endIndex > 0) {
      // Join the remaining lines after the front matter
      return lines.slice(endIndex + 1).join('\n').trim();
    }
    
    // If no closing --- found, return original content
    return content;
  }

  // Clean content for LLM (remove extra UI elements)
  function cleanContentForLLM(element) {
    const clone = element.cloneNode(true);
    
    // Remove buttons and UI elements
    clone.querySelectorAll('.md-clipboard, .copy-to-llm, .headerlink').forEach(el => el.remove());
    
    // Convert to markdown-like format
    let text = clone.innerHTML
      .replace(/<h1[^>]*>(.*?)<\/h1>/gi, '# $1\n\n')
      .replace(/<h2[^>]*>(.*?)<\/h2>/gi, '## $1\n\n')
      .replace(/<h3[^>]*>(.*?)<\/h3>/gi, '### $1\n\n')
      .replace(/<h4[^>]*>(.*?)<\/h4>/gi, '#### $1\n\n')
      .replace(/<pre[^>]*><code[^>]*>(.*?)<\/code><\/pre>/gs, '```\n$1\n```\n\n')
      .replace(/<code[^>]*>(.*?)<\/code>/g, '`$1`')
      .replace(/<strong[^>]*>(.*?)<\/strong>/g, '**$1**')
      .replace(/<em[^>]*>(.*?)<\/em>/g, '*$1*')
      .replace(/<a[^>]*href="([^"]*)"[^>]*>(.*?)<\/a>/g, '[$2]($1)')
      .replace(/<li[^>]*>(.*?)<\/li>/g, '- $1\n')
      .replace(/<p[^>]*>(.*?)<\/p>/g, '$1\n\n')
      .replace(/<br[^>]*>/g, '\n')
      .replace(/<[^>]+>/g, '');
    
    // Clean up extra whitespace
    return text.replace(/\n{3,}/g, '\n\n').trim();
  }

  // Copy to clipboard with fallback
  async function copyToClipboard(text, button) {
    try {
      await navigator.clipboard.writeText(text);
      showCopySuccess(button);
    } catch (err) {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      
      try {
        document.execCommand('copy');
        showCopySuccess(button);
      } catch (fallbackErr) {
        console.error('Failed to copy:', fallbackErr);
        showCopyError(button);
      }
      
      document.body.removeChild(textarea);
    }
  }

  // Show success feedback
  function showCopySuccess(button) {
    const originalTitle = button.title;
    const textElement = button.querySelector('.button-text');
    const originalText = textElement ? textElement.textContent : '';
    
    // Only change text for dropdown items, not the main copy button
    if (button.classList.contains('copy-to-llm-dropdown-item')) {
      button.classList.add('copy-success');
      button.title = 'Copied!';
      
      // If button has text, update it
      if (textElement) {
        textElement.textContent = 'Copied!';
      }
      
      setTimeout(() => {
        button.classList.remove('copy-success');
        button.title = originalTitle;
        if (textElement) {
          textElement.textContent = originalText;
        }
      }, 2000);
    }
    
    // Create and show toast notification
    const isMarkdownLink = button.classList.contains('copy-to-llm-dropdown-item') && 
                          button.dataset.action === 'copy-markdown-link';
    showToast(isMarkdownLink ? 'Link copied to clipboard!' : 'Content copied to clipboard!');
  }
  
  // Show toast notification
  function showToast(message) {
    // Remove any existing toast
    const existingToast = document.querySelector('.copy-to-llm-toast');
    if (existingToast) {
      existingToast.remove();
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = 'copy-to-llm-toast';
    toast.textContent = message;
    
    // Add to body
    document.body.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => {
      toast.classList.add('show');
    }, 10);
    
    // Remove after delay
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => {
        toast.remove();
      }, 300);
    }, 2500);
  }

  // Show error feedback
  function showCopyError(button) {
    button.classList.add('copy-error');
    button.title = 'Copy failed';
    
    setTimeout(() => {
      button.classList.remove('copy-error');
      button.title = 'Copy to LLM';
    }, 2000);
  }

  // Create copy to LLM button for code blocks
  function createCodeCopyButton() {
    const button = document.createElement('button');
    button.className = 'md-clipboard md-icon copy-to-llm copy-to-llm-code';
    button.title = 'Copy to LLM';
    button.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
      </svg>
    `;
    return button;
  }

  // Create copy to LLM button for sections
  function createSectionCopyButton() {
    // Create container for split button
    const container = document.createElement('div');
    container.className = 'copy-to-llm-split-container';
    
    // Left button (copy)
    const copyButton = document.createElement('button');
    copyButton.className = 'copy-to-llm copy-to-llm-section copy-to-llm-left';
    copyButton.title = 'Copy entire page to LLM';
    copyButton.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="copy-icon">
        <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
      </svg>
      <span class="button-text">Copy page</span>
    `;
    
    // Right button (dropdown)
    const dropdownButton = document.createElement('button');
    dropdownButton.className = 'copy-to-llm copy-to-llm-section copy-to-llm-right';
    dropdownButton.title = 'Copy options';
    dropdownButton.type = 'button'; // Explicitly set type
    dropdownButton.setAttribute('aria-label', 'Copy options menu');
    dropdownButton.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="chevron-icon">
        <path d="M7 10l5 5 5-5z"/>
      </svg>
    `;
    
    // Create dropdown menu
    const dropdownMenu = document.createElement('div');
    dropdownMenu.className = 'copy-to-llm-dropdown';
    dropdownMenu.innerHTML = `
      <button class="copy-to-llm-dropdown-item" data-action="copy-markdown-link">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
          <path d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z"/>
        </svg>
        Copy markdown link
      </button>
      <button class="copy-to-llm-dropdown-item" data-action="view-markdown">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
          <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
        </svg>
        <span>View as markdown</span>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="external-icon">
          <path d="M14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z"/>
        </svg>
      </button>
      <button class="copy-to-llm-dropdown-item" data-action="open-chatgpt">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
          <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/>
        </svg>
        <span>Open in ChatGPT</span>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="external-icon">
          <path d="M14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z"/>
        </svg>
      </button>
      <button class="copy-to-llm-dropdown-item" data-action="open-claude">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
        <span>Open in Claude</span>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="external-icon">
          <path d="M14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z"/>
        </svg>
      </button>
    `;
    
    container.appendChild(copyButton);
    container.appendChild(dropdownButton);
    container.appendChild(dropdownMenu);
    
    return { container, copyButton, dropdownButton, dropdownMenu };
  }

  // Add copy buttons to code blocks
  function addCodeCopyButtons() {
    const codeBlocks = document.querySelectorAll('.highlight');
    
    codeBlocks.forEach(block => {
      // Skip if button already exists
      if (block.querySelector('.copy-to-llm-code')) return;
      
      const preElement = block.querySelector('pre');
      if (!preElement) return;
      
      // Get language from class
      const codeElement = preElement.querySelector('code');
      const language = getLanguageFromClass(codeElement) || 'text';
      
      // Create and add button
      const button = createCodeCopyButton();
      button.addEventListener('click', (e) => {
        e.preventDefault();
        const formattedCode = formatCodeForLLM(codeElement, language);
        copyToClipboard(formattedCode, button);
      });
      
      // Insert after existing copy button if it exists
      const existingCopyBtn = block.querySelector('.md-clipboard');
      if (existingCopyBtn) {
        existingCopyBtn.parentNode.insertBefore(button, existingCopyBtn.nextSibling);
      } else {
        // Otherwise add to the code block
        block.appendChild(button);
      }
    });
  }

  // Get language from code element class
  function getLanguageFromClass(codeElement) {
    if (!codeElement || !codeElement.className) return null;
    
    const match = codeElement.className.match(/language-(\w+)/);
    return match ? match[1] : null;
  }

  // Add copy buttons to article sections
  function addSectionCopyButtons() {
    // Only add to the main h1 title
    const mainTitle = document.querySelector('.md-content h1');
    if (mainTitle && !document.querySelector('.copy-to-llm-split-container')) {
      // Create a wrapper div for h1 and button
      const wrapper = document.createElement('div');
      wrapper.className = 'h1-copy-wrapper';
      
      // Insert wrapper before h1
      mainTitle.parentNode.insertBefore(wrapper, mainTitle);
      
      // Move h1 into wrapper
      wrapper.appendChild(mainTitle);
      
      // Create and add split button
      const { container, copyButton, dropdownButton, dropdownMenu } = createSectionCopyButton();
      
      // Copy button click handler
      copyButton.addEventListener('click', async (e) => {
        e.preventDefault();
        
        // Save original icon HTML
        const copyIcon = copyButton.querySelector('.copy-icon');
        const originalIconHTML = copyIcon.outerHTML;
        
        // Replace icon with loading spinner
        copyIcon.outerHTML = `
          <svg class="copy-icon loading-spinner" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="31.4" stroke-dashoffset="0">
              <animate attributeName="stroke-dashoffset" dur="1s" repeatCount="indefinite" from="0" to="62.8"/>
            </circle>
          </svg>
        `;
        
        try {
          // Fetch the raw markdown content
          const mdUrl = getMdFileUrl();
          const response = await fetch(mdUrl);
          
          if (response.ok) {
            let markdownContent = await response.text();
            
            // Remove front matter (metadata) if present
            markdownContent = removeFrontMatter(markdownContent);
            
            await copyToClipboard(markdownContent, copyButton);
            
            // Change to check icon and make it green
            const checkIconSVG = `
              <svg class="copy-icon copy-success-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
              </svg>
            `;
            copyButton.querySelector('.copy-icon').outerHTML = checkIconSVG;
            
            // Restore original icon after 3 seconds
            setTimeout(() => {
              copyButton.querySelector('.copy-icon').outerHTML = originalIconHTML;
            }, 3000);
          } else {
            // Fallback to formatted content if fetch fails
            const articleContent = document.querySelector('.md-content__inner .md-typeset');
            if (articleContent) {
              const formattedContent = formatSectionForLLM(articleContent);
              await copyToClipboard(formattedContent, copyButton);
              
              // Restore original icon
              copyButton.querySelector('.copy-icon').outerHTML = originalIconHTML;
              
              // Show success by making icon green after a small delay to ensure DOM updates
              setTimeout(() => {
                copyButton.classList.add('copy-success-icon');
                setTimeout(() => {
                  copyButton.classList.remove('copy-success-icon');
                }, 3000);
              }, 50);
            }
          }
        } catch (error) {
          // Fallback to formatted content if fetch fails
          console.error('Failed to fetch markdown:', error);
          const articleContent = document.querySelector('.md-content__inner .md-typeset');
          if (articleContent) {
            const formattedContent = formatSectionForLLM(articleContent);
            await copyToClipboard(formattedContent, copyButton);
            
            // Change to check icon and make it green
            const checkIconSVG = `
              <svg class="copy-icon copy-success-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
              </svg>
            `;
            copyButton.querySelector('.copy-icon').outerHTML = checkIconSVG;
            
            // Restore original icon after 3 seconds
            setTimeout(() => {
              copyButton.querySelector('.copy-icon').outerHTML = originalIconHTML;
            }, 3000);
          }
        }
      });
      
      // Dropdown button click handler
      dropdownButton.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        console.log('Dropdown clicked!'); // Debug log
        dropdownMenu.classList.toggle('show');
        
        // Toggle chevron rotation
        const chevron = dropdownButton.querySelector('.chevron-icon');
        if (chevron) {
          chevron.style.transform = dropdownMenu.classList.contains('show') ? 'rotate(180deg)' : '';
        }
      });
      
      // Dropdown menu item handlers
      dropdownMenu.addEventListener('click', (e) => {
        e.stopPropagation();
        const item = e.target.closest('.copy-to-llm-dropdown-item');
        if (!item) return;
        
        const action = item.dataset.action;
        const articleContent = document.querySelector('.md-content__inner .md-typeset');
        let contentToCopy = '';
        
        switch(action) {
          case 'copy-markdown-link':
            // Copy the raw markdown file URL
            contentToCopy = getMdFileUrl();
            break;
            
          case 'view-markdown':
            // Open the raw markdown file directly
            const mdUrl = getMdFileUrl();
            window.open(mdUrl, '_blank');
            dropdownMenu.classList.remove('show');
            resetChevron();
            return; // Don't copy, just view
            
          case 'open-chatgpt':
            // Get the markdown file URL
            const mdUrlForChatGPT = getMdFileUrl();
            const chatGPTPrompt = `Read ${mdUrlForChatGPT} so I can ask questions about it.`;
            const chatGPTUrl = `https://chatgpt.com/?hints=search&q=${encodeURIComponent(chatGPTPrompt)}`;
            window.open(chatGPTUrl, '_blank');
            dropdownMenu.classList.remove('show');
            resetChevron();
            return; // Don't copy, just open
            
          case 'open-claude':
            // Get the markdown file URL
            const mdUrlForClaude = getMdFileUrl();
            const claudePrompt = `Read ${mdUrlForClaude} so I can ask questions about it.`;
            const claudeUrl = `https://claude.ai/new?q=${encodeURIComponent(claudePrompt)}`;
            window.open(claudeUrl, '_blank');
            dropdownMenu.classList.remove('show');
            resetChevron();
            return; // Don't copy, just open
        }
        
        if (contentToCopy) {
          copyToClipboard(contentToCopy, item);
          dropdownMenu.classList.remove('show');
          resetChevron();
        }
        
        function resetChevron() {
          const chevron = dropdownButton.querySelector('.chevron-icon');
          if (chevron) {
            chevron.style.transform = '';
          }
        }
      });
      
      // Close dropdown when clicking outside
      document.addEventListener('click', (e) => {
        if (!container.contains(e.target)) {
          dropdownMenu.classList.remove('show');
          // Reset chevron rotation
          const chevron = dropdownButton.querySelector('.chevron-icon');
          if (chevron) {
            chevron.style.transform = '';
          }
        }
      });
      
      wrapper.appendChild(container);
    }
  }

  // Get content of a section starting from a heading
  function getSectionContent(heading) {
    const content = document.createElement('div');
    content.appendChild(heading.cloneNode(true));
    
    let sibling = heading.nextElementSibling;
    while (sibling && !sibling.matches('h1, h2')) {
      content.appendChild(sibling.cloneNode(true));
      sibling = sibling.nextElementSibling;
    }
    
    return content;
  }

  // Initialize on DOM ready
  function initialize() {
    addCodeCopyButtons();
    addSectionCopyButtons();
    
    // Re-run when content changes (for dynamic content)
    const observer = new MutationObserver(() => {
      addCodeCopyButtons();
      addSectionCopyButtons();
    });
    
    const content = document.querySelector('.md-content');
    if (content) {
      observer.observe(content, {
        childList: true,
        subtree: true
      });
    }
  }

  // Wait for DOM to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
  } else {
    initialize();
  }

})();