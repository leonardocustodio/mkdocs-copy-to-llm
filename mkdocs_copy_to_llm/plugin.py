import os
import shutil
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from mkdocs import utils


class CopyToLLMPlugin(BasePlugin):
    """
    MkDocs plugin to add 'Copy to LLM' buttons to documentation
    """

    config_scheme = (
        ('enabled', config_options.Type(bool, default=True)),
        ('code_blocks', config_options.Type(bool, default=True)),
        ('page_button', config_options.Type(bool, default=True)),
    )

    def __init__(self):
        self.enabled = True

    def on_config(self, config, **kwargs):
        """
        Called after the user configuration is loaded
        """
        if not self.config.get('enabled', True):
            return config

        # Store the config for later use
        self.enabled = True
        
        # Get the path to our assets
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        js_path = os.path.join(plugin_dir, 'assets', 'js', 'copy-to-llm.js')
        css_path = os.path.join(plugin_dir, 'assets', 'css', 'copy-to-llm.css')
        
        # Add our JS to extra_javascript if it exists
        if 'extra_javascript' not in config:
            config['extra_javascript'] = []
        
        # Add our CSS to extra_css if it exists
        if 'extra_css' not in config:
            config['extra_css'] = []
            
        # We'll inject these paths later when we copy the files
        self.js_path = 'assets/copy-to-llm/copy-to-llm.js'
        self.css_path = 'assets/copy-to-llm/copy-to-llm.css'
        
        config['extra_javascript'].append(self.js_path)
        config['extra_css'].append(self.css_path)
            
        return config

    def on_pre_build(self, config):
        """
        Called before the build process starts
        """
        if not self.enabled:
            return
        
        # Copy our assets to the docs directory so they're included in the build
        docs_dir = config['docs_dir']
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create assets directory in docs
        assets_dir = os.path.join(docs_dir, 'assets', 'copy-to-llm')
        os.makedirs(assets_dir, exist_ok=True)
        
        # Copy JS file
        js_src = os.path.join(plugin_dir, 'assets', 'js', 'copy-to-llm.js')
        if os.path.exists(js_src):
            js_dest = os.path.join(assets_dir, 'copy-to-llm.js')
            shutil.copy2(js_src, js_dest)
            utils.log.info(f"Copied Copy to LLM JS to {js_dest}")
        else:
            utils.log.warning(f"Copy to LLM JS file not found at {js_src}")
        
        # Copy CSS file
        css_src = os.path.join(plugin_dir, 'assets', 'css', 'copy-to-llm.css')
        if os.path.exists(css_src):
            css_dest = os.path.join(assets_dir, 'copy-to-llm.css')
            shutil.copy2(css_src, css_dest)
            utils.log.info(f"Copied Copy to LLM CSS to {css_dest}")
        else:
            utils.log.warning(f"Copy to LLM CSS file not found at {css_src}")

    def on_post_build(self, config):
        """
        Called after the build is complete - clean up temporary files
        """
        if not self.enabled:
            return
        
        # Clean up the temporary assets we copied to docs_dir
        docs_dir = config['docs_dir']
        assets_dir = os.path.join(docs_dir, 'assets', 'copy-to-llm')
        
        if os.path.exists(assets_dir):
            shutil.rmtree(assets_dir)
            utils.log.info("Cleaned up temporary Copy to LLM assets")