import React, { createContext, useContext, useState, useEffect } from 'react';

export interface Document {
  id: string;
  name: string;
  type: string;
  size: number;
  uploadDate: string;
  preview?: string;
  extractedText?: string;
  userId: string;
}

interface DocumentContextType {
  documents: Document[];
  addDocument: (doc: Omit<Document, 'id' | 'uploadDate'>) => void;
  deleteDocument: (id: string) => void;
  getDocument: (id: string) => Document | undefined;
}

const DocumentContext = createContext<DocumentContextType | undefined>(undefined);

export const DocumentProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [documents, setDocuments] = useState<Document[]>([]);

  useEffect(() => {
    const stored = localStorage.getItem('documents');
    if (stored) {
      setDocuments(JSON.parse(stored));
    }
  }, []);

  const addDocument = (doc: Omit<Document, 'id' | 'uploadDate'>) => {
    const newDoc: Document = {
      ...doc,
      id: crypto.randomUUID(),
      uploadDate: new Date().toISOString(),
    };
    const updated = [...documents, newDoc];
    setDocuments(updated);
    localStorage.setItem('documents', JSON.stringify(updated));
  };

  const deleteDocument = (id: string) => {
    const updated = documents.filter(d => d.id !== id);
    setDocuments(updated);
    localStorage.setItem('documents', JSON.stringify(updated));
  };

  const getDocument = (id: string) => {
    return documents.find(d => d.id === id);
  };

  return (
    <DocumentContext.Provider value={{ documents, addDocument, deleteDocument, getDocument }}>
      {children}
    </DocumentContext.Provider>
  );
};

export const useDocuments = () => {
  const context = useContext(DocumentContext);
  if (!context) {
    throw new Error('useDocuments must be used within DocumentProvider');
  }
  return context;
};
