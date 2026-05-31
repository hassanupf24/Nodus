import React, { useCallback } from 'react';

interface FileDropzoneProps {
  children: React.ReactNode;
}

export const FileDropzone: React.FC<FileDropzoneProps> = ({ children }) => {
  const onDrop = useCallback(async (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      const formData = new FormData();
      formData.append('file', file);
      
      try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/ingest/file', {
          method: 'POST',
          body: formData,
        });
        const result = await response.json();
        console.log("File ingested:", result);
      } catch (err) {
        console.error("Ingestion failed", err);
      }
    }
  }, []);

  const onDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  return (
    <div 
      onDrop={onDrop} 
      onDragOver={onDragOver} 
      className="h-full w-full"
    >
      {children}
    </div>
  );
};
