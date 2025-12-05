import { useState, useCallback } from 'react';
import { DashboardLayout } from '@/components/DashboardLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useDocuments } from '@/contexts/DocumentContext';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';
import { Upload as UploadIcon, FileText, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Upload() {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const { addDocument } = useDocuments();
  const { user } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();

  const handleFile = useCallback((file: File) => {
    if (!file.type.match(/^(image\/(jpeg|jpg|png|webp)|application\/pdf)$/)) {
      toast({
        title: 'Invalid file type',
        description: 'Please upload an image (JPG, PNG, WEBP) or PDF file',
        variant: 'destructive',
      });
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      toast({
        title: 'File too large',
        description: 'Maximum file size is 10MB',
        variant: 'destructive',
      });
      return;
    }

    setSelectedFile(file);

    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target?.result as string);
      reader.readAsDataURL(file);
    } else {
      setPreview(null);
    }
  }, [toast]);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !user) return;

    setIsUploading(true);

    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 1500));

    const mockExtractedText = selectedFile.type === 'application/pdf'
      ? 'Sample extracted text from PDF document. This is a demonstration of the text extraction feature.'
      : 'Image uploaded successfully. Text extraction would be performed here in a production environment.';

    addDocument({
      name: selectedFile.name,
      type: selectedFile.type,
      size: selectedFile.size,
      preview: preview || undefined,
      extractedText: mockExtractedText,
      userId: user.id,
    });

    toast({
      title: 'Success!',
      description: 'Document uploaded and processed successfully',
    });

    setIsUploading(false);
    navigate('/documents');
  };

  return (
    <DashboardLayout>
      <div className="max-w-2xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Upload Document</h1>
          <p className="text-muted-foreground">Upload images or PDFs to extract information</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Select File</CardTitle>
            <CardDescription>Drag and drop or click to select a file (JPG, PNG, WEBP, PDF)</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div
              className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors cursor-pointer ${
                dragActive ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => document.getElementById('file-input')?.click()}
            >
              <UploadIcon className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-lg font-medium mb-1">Drop your file here</p>
              <p className="text-sm text-muted-foreground">or click to browse</p>
              <input
                id="file-input"
                type="file"
                className="hidden"
                accept="image/jpeg,image/jpg,image/png,image/webp,application/pdf"
                onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
              />
            </div>

            {selectedFile && (
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3 flex-1">
                      {preview ? (
                        <img src={preview} alt="Preview" className="h-20 w-20 rounded object-cover" />
                      ) : (
                        <div className="h-20 w-20 rounded bg-muted flex items-center justify-center">
                          <FileText className="h-8 w-8 text-muted-foreground" />
                        </div>
                      )}
                      <div className="flex-1">
                        <p className="font-medium">{selectedFile.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {(selectedFile.size / 1024).toFixed(1)} KB
                        </p>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        setSelectedFile(null);
                        setPreview(null);
                      }}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            <Button
              onClick={handleUpload}
              disabled={!selectedFile || isUploading}
              className="w-full"
              size="lg"
            >
              {isUploading ? 'Processing...' : 'Upload and Process'}
            </Button>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
