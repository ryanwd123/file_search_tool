import QtQuick 2.15
import QtQuick.Controls 2.15

// import "viewers" as Vf

Rectangle {
    id: root
    anchors.fill: parent
    property int sizing: 20
    // id: viewerWindow

    // File type mappings
    readonly property var fileTypeMap: {
        '.pdf': 'pdf',
        '.txt': 'text',
        '.md': 'text',
        '.json': 'text',
        '.py': 'text',
        '.js': 'text',
        '.html': 'text',
        '.css': 'text',
        '.xml': 'text',
        '.yml': 'text',
        '.yaml': 'text',
        '.sql': 'text',
        '.qml': 'text',
        '.ts': 'text',
        '.log': 'text',
        '.ini': 'text',
        '.cfg': 'text',
        '.conf': 'text',
        '.png': 'image',
        '.jpg': 'image',
        '.jpeg': 'image',
        '.gif': 'image',
        '.bmp': 'image',
        '.tiff': 'image',
        '.tif': 'image',
        '.webp': 'image'
    }

    // Component source mappings
    readonly property var componentMap: {
        'pdf': 'viewers/PdfViewerComponent.qml',
        'text': 'viewers/TextViewerComponent.qml',
        'image': 'viewers/ImageViewerComponent.qml'
    }

    // Function to open a file in the viewer
    function openFileInViewer(filePath) {
        if (!filePath) {
            console.log("No file path provided");
            return false;
        }

        // Extract file extension
        let lastDotIndex = filePath.lastIndexOf('.');
        if (lastDotIndex === -1) {
            console.log("No file extension found for:", filePath);
            return false;
        }

        let extension = filePath.substring(lastDotIndex).toLowerCase();
        let fileType = fileTypeMap[extension];

        if (!fileType) {
            console.log("Unsupported file type:", extension);
            return false;
        }

        // Check if component exists for this file type
        if (!componentMap[fileType]) {
            console.log("No component available for file type:", fileType);
            return false;
        }

        if (loader.source != componentMap[fileType]) {
            loader.source = componentMap[fileType];
        }
        loader.item.filePath = filePath;
    }

    Loader {
        id: loader
        anchors.fill: parent
    }
}
