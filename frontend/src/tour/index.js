import { driver } from "driver.js";
import "driver.js/dist/driver.css";

export const createTour = () => {
    const driverObj = driver({
        showProgress: true,
        animate: true,
        allowClose: true,
        doneBtnText: 'Done',
        closeBtnText: 'Skip',
        nextBtnText: 'Next',
        prevBtnText: 'Previous',
        steps: [
            {
                element: '#tour-welcome',
                popover: {
                    title: 'Welcome to Brain Vault',
                    description: 'Your personal AI-powered knowledge base. Let us show you around!',
                    side: "bottom",
                    align: 'start'
                }
            },
            {
                element: '#tour-knowledge-base',
                popover: {
                    title: 'Knowledge Base',
                    description: 'Here you can see all your stored memories and uploaded documents. Click on any item to view or edit it.',
                    side: "right",
                    align: 'start'
                }
            },
            {
                element: '#tour-quick-actions',
                popover: {
                    title: 'Quick Actions',
                    description: 'Quickly add new memories, notes, or ideas. Just type and save!',
                    side: "bottom",
                    align: 'start'
                }
            },
            {
                element: '#tour-upload',
                popover: {
                    title: 'Upload Files',
                    description: 'Upload PDF, TXT, or Markdown files to expand your knowledge base.',
                    side: "left",
                    align: 'start'
                }
            },
            {
                element: '#tour-retrieval',
                popover: {
                    title: 'Ask Your Brain',
                    description: 'Chat with your knowledge base! Ask questions and get answers based on your stored memories and documents.',
                    side: "left",
                    align: 'start'
                }
            },
            {
                element: '#tour-memory-map',
                popover: {
                    title: 'Memory Map',
                    description: 'Visualize connections between your memories and documents in an interactive map.',
                    side: "bottom",
                    align: 'start'
                }
            },
            {
                element: '#tour-settings',
                popover: {
                    title: 'Settings',
                    description: 'Configure your API keys, export your data, and manage your account settings here.',
                    side: "bottom",
                    align: 'end'
                }
            }
        ]
    });

    return driverObj;
};
