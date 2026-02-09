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
                    title: 'Welcome to MemWyre',
                    description: 'Your personal AI-powered knowledge base. Let us show you around!',
                    side: "bottom",
                    align: 'start'
                }
            },
            {
                element: '#tour-knowledge-base',
                popover: {
                    title: 'Your Memories',
                    description: 'This is your central knowledge base. All your memories and documents are stored here for easy access.',
                    side: "right",
                    align: 'start'
                }
            },
            {
                element: '#tour-quick-actions',
                popover: {
                    title: 'Quick Add',
                    description: 'Capture new ideas, upload documents, or clip web pages instantly.',
                    side: "bottom",
                    align: 'start'
                }
            },
            {
                element: '#tour-inbox',
                popover: {
                    title: 'Inbox',
                    description: 'Review new incoming memories or processing tasks.',
                    side: "bottom",
                    align: 'center'
                }
            },
            {
                element: '#tour-retrieval',
                popover: {
                    title: 'Chat with MemWyre',
                    description: 'Ask questions and get answers based on your knowledge base.',
                    side: "bottom",
                    align: 'center'
                }
            },
            {
                element: '#tour-memory-map',
                popover: {
                    title: 'Memory Map',
                    description: 'Visualize how your memories connect in an interactive graph.',
                    side: "bottom",
                    align: 'center'
                }
            }
        ]
    });

    return driverObj;
};
