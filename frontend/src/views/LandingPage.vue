<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
    <!-- Navigation -->
    <nav class="fixed w-full z-50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-800">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center">
            <svg class="h-8 w-8 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <span class="ml-2 text-xl font-bold text-gray-900 dark:text-white">Brain Vault</span>
          </div>
          <div class="flex items-center space-x-4">
            <router-link to="/login" class="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white font-medium transition-colors">
              Log in
            </router-link>
            <router-link to="/register" class="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-medium transition-colors shadow-lg shadow-indigo-500/30">
              Get Started
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <div class="relative pt-32 pb-20 sm:pt-40 sm:pb-24 overflow-hidden">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
        <h1 class="text-5xl sm:text-7xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600 dark:from-indigo-400 dark:to-violet-400 tracking-tight mb-8">
          Your Second Brain,<br />
          <span class="text-gray-900 dark:text-white">Supercharged with AI.</span>
        </h1>
        <p class="mt-4 max-w-2xl mx-auto text-xl text-gray-500 dark:text-gray-400 mb-10">
          Capture thoughts, store documents, and chat with your personal knowledge base. Secure, private, and always accessible.
        </p>
        <div class="flex justify-center gap-4">
          <router-link to="/register" class="px-8 py-4 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-lg font-bold transition-all transform hover:scale-105 shadow-xl shadow-indigo-500/40">
            Start Building Your Brain
          </router-link>
          <a href="#features" class="px-8 py-4 rounded-xl bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-lg font-bold border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-all">
            Learn More
          </a>
        </div>
      </div>
      
      <!-- Background Blobs -->
      <div class="absolute top-0 left-1/2 w-full -translate-x-1/2 h-full z-0 pointer-events-none">
        <div class="absolute top-20 left-10 w-72 h-72 bg-purple-300 dark:bg-purple-900 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
        <div class="absolute top-20 right-10 w-72 h-72 bg-indigo-300 dark:bg-indigo-900 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-2000"></div>
        <div class="absolute -bottom-8 left-1/2 w-72 h-72 bg-pink-300 dark:bg-pink-900 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-4000"></div>
      </div>
    </div>

    <!-- Features Section -->
    <div id="features" class="py-24 bg-white dark:bg-gray-800/50 relative">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2 class="text-base text-indigo-600 dark:text-indigo-400 font-semibold tracking-wide uppercase">Features</h2>
          <p class="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
            Everything you need to remember
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-10">
          <!-- Feature 1 -->
          <div class="p-8 rounded-2xl bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 hover:shadow-2xl transition-shadow duration-300">
            <div class="w-12 h-12 bg-indigo-100 dark:bg-indigo-900/50 rounded-lg flex items-center justify-center mb-6">
              <svg class="w-6 h-6 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-3">Memory Map</h3>
            <p class="text-gray-500 dark:text-gray-400">
              Visualize your thoughts and connections. Our intelligent tagging system links related concepts automatically.
            </p>
          </div>

          <!-- Feature 2 -->
          <div class="p-8 rounded-2xl bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 hover:shadow-2xl transition-shadow duration-300">
            <div class="w-12 h-12 bg-purple-100 dark:bg-purple-900/50 rounded-lg flex items-center justify-center mb-6">
              <svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-3">AI Chat</h3>
            <p class="text-gray-500 dark:text-gray-400">
              Chat with your documents. Ask questions and get answers based on your personal knowledge base.
            </p>
          </div>

          <!-- Feature 3 -->
          <div class="p-8 rounded-2xl bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 hover:shadow-2xl transition-shadow duration-300">
            <div class="w-12 h-12 bg-emerald-100 dark:bg-emerald-900/50 rounded-lg flex items-center justify-center mb-6">
              <svg class="w-6 h-6 text-emerald-600 dark:text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-3">Secure & Private</h3>
            <p class="text-gray-500 dark:text-gray-400">
              Your data is yours. We prioritize security and privacy, ensuring your second brain remains personal.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Real Life Workflows Section -->
    <div class="py-24 bg-gray-50 dark:bg-gray-900 relative overflow-hidden">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div class="text-center mb-16">
          <h2 class="text-base text-indigo-600 dark:text-indigo-400 font-semibold tracking-wide uppercase">Use Cases</h2>
          <p class="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
            See it in action
          </p>
        </div>

        <div class="space-y-20">
          <!-- Workflow 1: The Researcher -->
          <div class="flex flex-col lg:flex-row items-center gap-12">
            <div class="flex-1 order-2 lg:order-1">
              <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 border border-gray-100 dark:border-gray-700">
                <div class="flex items-center space-x-4 mb-6">
                  <div class="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold">1</div>
                  <h4 class="text-lg font-semibold text-gray-900 dark:text-white">Upload Research Papers</h4>
                </div>
                <div class="flex items-center space-x-4 mb-6">
                  <div class="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold">2</div>
                  <h4 class="text-lg font-semibold text-gray-900 dark:text-white">Highlight Key Insights</h4>
                </div>
                <div class="flex items-center space-x-4">
                  <div class="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold">3</div>
                  <h4 class="text-lg font-semibold text-gray-900 dark:text-white">Ask AI to Synthesize</h4>
                </div>
              </div>
            </div>
            <div class="flex-1 order-1 lg:order-2">
              <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">The Researcher</h3>
              <p class="text-lg text-gray-500 dark:text-gray-400 mb-6">
                "I used to drown in PDFs. Now, I simply upload them to Brain Vault. I can ask complex questions across multiple papers and get cited answers instantly. It's like having a research assistant who never sleeps."
              </p>
              <ul class="space-y-3 text-gray-500 dark:text-gray-400">
                <li class="flex items-center">
                  <svg class="h-5 w-5 text-green-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                  Cross-document analysis
                </li>
                <li class="flex items-center">
                  <svg class="h-5 w-5 text-green-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                  Instant citation generation
                </li>
              </ul>
            </div>
          </div>

          <!-- Workflow 2: The Developer -->
          <div class="flex flex-col lg:flex-row items-center gap-12">
            <div class="flex-1">
              <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">The Developer</h3>
              <p class="text-lg text-gray-500 dark:text-gray-400 mb-6">
                "Documenting code is a chore. With Brain Vault, I save snippets, architecture diagrams, and error logs. When a bug pops up, I ask my vault, and it finds the relevant context and suggests a fix."
              </p>
              <ul class="space-y-3 text-gray-500 dark:text-gray-400">
                <li class="flex items-center">
                  <svg class="h-5 w-5 text-green-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                  Context-aware debugging
                </li>
                <li class="flex items-center">
                  <svg class="h-5 w-5 text-green-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                  Knowledge retention
                </li>
              </ul>
            </div>
            <div class="flex-1">
              <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 border border-gray-100 dark:border-gray-700">
                <div class="font-mono text-sm text-gray-800 dark:text-gray-200 bg-gray-100 dark:bg-gray-900 p-4 rounded-lg mb-4">
                  <span class="text-purple-600">Error:</span> Connection refused at port 5432<br>
                  <span class="text-gray-500">...searching knowledge base...</span>
                </div>
                <div class="flex items-start space-x-3">
                  <div class="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-xs">AI</div>
                  <div class="bg-indigo-50 dark:bg-indigo-900/30 p-4 rounded-lg rounded-tl-none text-sm text-gray-800 dark:text-gray-200">
                    Based on your "Docker Setup" note from last week, you need to expose the port in your docker-compose.yml file.
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Workflow 3: The Creator -->
          <div class="flex flex-col lg:flex-row items-center gap-12">
            <div class="flex-1 order-2 lg:order-1">
              <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 border border-gray-100 dark:border-gray-700 relative">
                <div class="absolute -top-4 -right-4 bg-yellow-400 text-yellow-900 text-xs font-bold px-3 py-1 rounded-full shadow-lg">Idea Spark!</div>
                <div class="grid grid-cols-2 gap-4">
                  <div class="bg-pink-100 dark:bg-pink-900/30 p-4 rounded-lg text-center">
                    <svg class="w-8 h-8 mx-auto text-pink-600 dark:text-pink-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                    </svg>
                    <p class="text-sm font-medium mt-2 text-gray-900 dark:text-white">Design</p>
                  </div>
                  <div class="bg-green-100 dark:bg-green-900/30 p-4 rounded-lg text-center">
                    <svg class="w-8 h-8 mx-auto text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    <p class="text-sm font-medium mt-2 text-gray-900 dark:text-white">Copy</p>
                  </div>
                  <div class="bg-orange-100 dark:bg-orange-900/30 p-4 rounded-lg text-center col-span-2">
                    <svg class="w-8 h-8 mx-auto text-orange-600 dark:text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    <p class="text-sm font-medium mt-2 text-gray-900 dark:text-white">Launch Strategy</p>
                  </div>
                </div>
              </div>
            </div>
            <div class="flex-1 order-1 lg:order-2">
              <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">The Creator</h3>
              <p class="text-lg text-gray-500 dark:text-gray-400 mb-6">
                "Inspiration strikes at weird times. I capture fleeting thoughts in Brain Vault. Later, I use the Memory Map to connect these loose ideas into a cohesive project plan."
              </p>
              <ul class="space-y-3 text-gray-500 dark:text-gray-400">
                <li class="flex items-center">
                  <svg class="h-5 w-5 text-green-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                  Visual idea linking
                </li>
                <li class="flex items-center">
                  <svg class="h-5 w-5 text-green-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                  Brainstorming partner
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>



    <!-- Integrations Section -->
    <div class="py-24 bg-white dark:bg-gray-800">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2 class="text-base text-indigo-600 dark:text-indigo-400 font-semibold tracking-wide uppercase">Ecosystem</h2>
          <p class="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
            Connect your world
          </p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-16">
          <!-- MCP Server -->
          <div class="flex flex-col items-center text-center p-8 rounded-3xl bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 border border-gray-200 dark:border-gray-600">
            <div class="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-blue-500/30">
              <svg class="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">Power Your AI</h3>
            <p class="text-gray-600 dark:text-gray-300 mb-8">
              Brain Vault implements the <strong>Model Context Protocol (MCP)</strong>. Connect directly to Claude Desktop or other LLM interfaces to give your AI access to your personal knowledge base.
            </p>
            <div class="bg-gray-900 rounded-lg p-4 text-left w-full max-w-md shadow-inner font-mono text-xs sm:text-sm text-green-400 overflow-x-auto">
              <div class="flex items-center mb-2 border-b border-gray-700 pb-2">
                <span class="w-3 h-3 rounded-full bg-red-500 mr-2"></span>
                <span class="w-3 h-3 rounded-full bg-yellow-500 mr-2"></span>
                <span class="w-3 h-3 rounded-full bg-green-500"></span>
              </div>
              <p>$ mcp-server-brain-vault start</p>
              <p class="text-gray-500">Starting server on port 8000...</p>
              <p class="text-blue-400">✓ Connected to Claude Desktop</p>
            </div>
          </div>

          <!-- Browser Extension -->
          <div class="flex flex-col items-center text-center p-8 rounded-3xl bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 border border-gray-200 dark:border-gray-600">
            <div class="w-16 h-16 bg-purple-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-purple-500/30">
              <svg class="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
              </svg>
            </div>
            <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">Capture Everywhere</h3>
            <p class="text-gray-600 dark:text-gray-300 mb-8">
              Don't break your flow. Use our <strong>Browser Extension</strong> to instantly save articles, documentation, or random thoughts directly to your vault without leaving the page.
            </p>
            <div class="relative w-full max-w-xs mx-auto">
              <div class="absolute -inset-1 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg blur opacity-25"></div>
              <div class="relative bg-white dark:bg-gray-900 rounded-lg p-4 shadow-xl border border-gray-200 dark:border-gray-700 text-left">
                <div class="flex items-center justify-between mb-4 border-b border-gray-200 dark:border-gray-800 pb-2">
                  <span class="font-bold text-gray-900 dark:text-white">Brain Vault</span>
                  <span class="w-2 h-2 bg-green-500 rounded-full"></span>
                </div>
                <div class="space-y-2">
                  <div class="h-8 bg-gray-100 dark:bg-gray-800 rounded w-full flex items-center px-2 text-xs text-gray-500">Save Selection</div>
                  <div class="h-8 bg-indigo-600 rounded w-full flex items-center justify-center text-xs text-white font-bold">Save Page</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <footer class="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 py-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center">
        <p class="text-gray-500 dark:text-gray-400">© 2025 Brain Vault. All rights reserved.</p>
        <div class="flex space-x-6">
          <a href="#" class="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300">
            <span class="sr-only">GitHub</span>
            <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd" />
            </svg>
          </a>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.animate-blob {
  animation: blob 7s infinite;
}
.animation-delay-2000 {
  animation-delay: 2s;
}
.animation-delay-4000 {
  animation-delay: 4s;
}
@keyframes blob {
  0% { transform: translate(0px, 0px) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0px, 0px) scale(1); }
}
</style>
