import { useState } from 'react';
import { DashboardLayout } from '@/components/DashboardLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useDocuments } from '@/contexts/DocumentContext';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';
import { FileText, Search, Trash2, Eye, Grid3x3, List } from 'lucide-react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';

export default function Documents() {
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedDoc, setSelectedDoc] = useState<any>(null);
  const { documents, deleteDocument } = useDocuments();
  const { user } = useAuth();
  const { toast } = useToast();

  const userDocs = documents.filter(d => d.userId === user?.id);
  const filteredDocs = userDocs.filter(doc =>
    doc.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleDelete = (id: string, name: string) => {
    deleteDocument(id);
    toast({ title: 'Document deleted', description: `${name} has been removed` });
    setSelectedDoc(null);
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Documents</h1>
          <p className="text-muted-foreground">Manage and view your uploaded documents</p>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search documents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
          <div className="flex gap-2">
            <Button
              variant={viewMode === 'grid' ? 'default' : 'outline'}
              size="icon"
              onClick={() => setViewMode('grid')}
            >
              <Grid3x3 className="h-4 w-4" />
            </Button>
            <Button
              variant={viewMode === 'list' ? 'default' : 'outline'}
              size="icon"
              onClick={() => setViewMode('list')}
            >
              <List className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {filteredDocs.length === 0 ? (
          <Card>
            <CardContent className="pt-6 text-center py-12">
              <FileText className="mx-auto h-12 w-12 text-muted-foreground mb-4 opacity-50" />
              <p className="text-lg font-medium mb-1">No documents found</p>
              <p className="text-sm text-muted-foreground">
                {searchQuery ? 'Try a different search term' : 'Upload your first document to get started'}
              </p>
            </CardContent>
          </Card>
        ) : viewMode === 'grid' ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {filteredDocs.map((doc) => (
              <Card key={doc.id} className="overflow-hidden hover:shadow-md transition-shadow cursor-pointer">
                <div
                  className="aspect-video bg-muted flex items-center justify-center"
                  onClick={() => setSelectedDoc(doc)}
                >
                  {doc.preview ? (
                    <img src={doc.preview} alt={doc.name} className="w-full h-full object-cover" />
                  ) : (
                    <FileText className="h-12 w-12 text-muted-foreground" />
                  )}
                </div>
                <CardContent className="p-4">
                  <p className="font-medium truncate mb-1">{doc.name}</p>
                  <p className="text-xs text-muted-foreground mb-3">
                    {new Date(doc.uploadDate).toLocaleDateString()} • {(doc.size / 1024).toFixed(1)} KB
                  </p>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      className="flex-1"
                      onClick={() => setSelectedDoc(doc)}
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleDelete(doc.id, doc.name)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="space-y-2">
            {filteredDocs.map((doc) => (
              <Card key={doc.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-4 flex items-center justify-between">
                  <div className="flex items-center gap-4 flex-1">
                    {doc.preview ? (
                      <img src={doc.preview} alt={doc.name} className="h-12 w-12 rounded object-cover" />
                    ) : (
                      <div className="h-12 w-12 rounded bg-muted flex items-center justify-center">
                        <FileText className="h-6 w-6 text-muted-foreground" />
                      </div>
                    )}
                    <div className="flex-1">
                      <p className="font-medium">{doc.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {new Date(doc.uploadDate).toLocaleDateString()} • {(doc.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" onClick={() => setSelectedDoc(doc)}>
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleDelete(doc.id, doc.name)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        <Dialog open={!!selectedDoc} onOpenChange={() => setSelectedDoc(null)}>
          <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>{selectedDoc?.name}</DialogTitle>
              <DialogDescription>
                Uploaded on {selectedDoc && new Date(selectedDoc.uploadDate).toLocaleDateString()}
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              {selectedDoc?.preview && (
                <img
                  src={selectedDoc.preview}
                  alt={selectedDoc.name}
                  className="w-full rounded-lg"
                />
              )}
              {selectedDoc?.extractedText && (
                <div>
                  <h3 className="font-semibold mb-2">Extracted Information</h3>
                  <Card>
                    <CardContent className="p-4">
                      <p className="text-sm whitespace-pre-wrap">{selectedDoc.extractedText}</p>
                    </CardContent>
                  </Card>
                </div>
              )}
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  );
}
