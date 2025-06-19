import QtQuick
import QtQuick.Pdf

Rectangle {
    id: pdfViewerComponent

    property string filePath: ""
    property int sizing: 20

    // required property string filePath

    color: "#ffffff"

    onFilePathChanged: {
        if (filePath !== "") {
            pdf.document.source = "file:///" + filePath
            pdf_rect.scale_to_width()
        }
    }


    Rectangle {
        id:pdf_rect
        anchors.fill: parent
        onWidthChanged: scale_to_width()

        // Top bar with page indicators
        Rectangle {
            id: topBar
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: 30
            color: "#f0f0f0"
            border.color: "#d0d0d0"
            border.width: 1
            z: 1

            Text {
                id: pageIndicator
                anchors.centerIn: parent
                text: pdf.document.status === PdfDocument.Ready ? "Page " + (pdf.currentPage + 1) + " of " + pdf.document.pageCount : "Loading..."
                font.pixelSize: 14
                font.family: "Arial"
                color: "#333333"
            }

            Text {
                anchors.right: search_rect.left
                anchors.verticalCenter: search_rect.verticalCenter
                text: 'Search (Enter/Shift+Enter)  '
                font.pixelSize: 14
            }

            Rectangle {
                id: search_rect
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.rightMargin: 10
                height: search.implicitHeight + 4
                width: 200
                color: 'white'
                border.color: "#d0d0d0"
                border.width: 1

                TextInput {
                    id: search
                    anchors.fill: parent
                    anchors.margins: 2
                    font.pixelSize: 14
                    verticalAlignment: TextInput.AlignVCenter
                    onActiveFocusChanged: {
                        console.log("focus");
                    }

                    Shortcut {
                        sequences: ['Return']
                        enabled: search.activeFocus
                        onActivated: {
                            if (pdf.searchString != search.text) {
                                pdf.searchString = search.text;
                            }
                            pdf.searchForward();
                        }
                    }

                    Shortcut {
                        sequences: ['Shift+Return']
                        enabled: search.activeFocus
                        onActivated: {
                            if (pdf.searchString != search.text) {
                                pdf.searchString = search.text;
                            }
                            pdf.searchBack();
                        }
                    }
                }
            }
        }

        PdfMultiPageView {
            id: pdf
            clip: true
            anchors.top: topBar.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom

            document: PdfDocument {
                source: "file:///" + ""
            }
        }

        function scale_to_width() {
            // Calculate scale to fit width
            if (pdf.document.status === PdfDocument.Ready && pdf.document.pageCount > 0) {
                var pageSize = pdf.document.pagePointSize(0);
                var availableWidth = parent.width;
                var scale = (availableWidth / pageSize.width) - 0.02;
                console.log("PDF scale:", scale);
                pdf.renderScale = scale;
            }
        }

    }

    // Keyboard shortcuts for PDF navigation
    Shortcut {
        sequences: ["Page Down", "Space"]
        onActivated: {
            if (pdf.currentPage < pdf.document.pageCount - 1) {
                console.log('pgdown')
                pdf.goToPage(pdf.currentPage+1);
            }
        }
    }

    Shortcut {
        sequences: ["Page Up", "Shift+Space"]
        onActivated: {
            if (pdf.currentPage > 0) {
                pdf.currentPage--;
            }
        }
    }

    Shortcut {
        sequences: ["Home"]
        onActivated: {
            pdf.currentPage = 0;
        }
    }

    Shortcut {
        sequences: ["End"]
        onActivated: {
            pdf.currentPage = pdf.document.pageCount - 1;
        }
    }

    Shortcut {
        sequences: ["Ctrl+=", "Ctrl+Plus"]
        onActivated: {
            pdf.renderScale = Math.min(pdf.renderScale * 1.2, 5.0);
        }
    }

    Shortcut {
        sequences: ["Ctrl+-", "Ctrl+Minus"]
        onActivated: {
            pdf.renderScale = Math.max(pdf.renderScale / 1.2, 0.1);
        }
    }

    Shortcut {
        sequences: ["Ctrl+0"]
        onActivated: {
            pdf_rect.scale_to_width();
        }
    }
}
