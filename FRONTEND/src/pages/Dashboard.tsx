import { DashboardLayout } from '@/components/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { useDocuments } from '@/contexts/DocumentContext';
import { FileText, Upload, Clock } from 'lucide-react';

export default function Dashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { documents } = useDocuments();

  const userDocs = documents.filter(d => d.userId === user?.id);
  const recentDocs = userDocs.slice(-3).reverse();

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Welcome back, {user?.name}!</h1>
          <p className="text-muted-foreground">Here's an overview of your documents</p>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Total Documents</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{userDocs.length}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">This Month</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {userDocs.filter(d => {
                  const docDate = new Date(d.uploadDate);
                  const now = new Date();
                  return docDate.getMonth() === now.getMonth() && docDate.getFullYear() === now.getFullYear();
                }).length}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Quick Upload</CardTitle>
              <Upload className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <Button onClick={() => navigate('/upload')} className="w-full">
                Upload Document
              </Button>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Recent Documents</CardTitle>
          </CardHeader>
          <CardContent>
            {recentDocs.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <FileText className="mx-auto h-12 w-12 mb-2 opacity-50" />
                <p>No documents yet. Upload your first document to get started!</p>
              </div>
            ) : (
              <div className="space-y-3">
                {recentDocs.map((doc) => (
                  <div
                    key={doc.id}
                    className="flex items-center justify-between rounded-lg border p-3 hover:bg-muted/50 cursor-pointer transition-colors"
                    onClick={() => navigate('/documents')}
                  >
                    <div className="flex items-center gap-3">
                      <FileText className="h-5 w-5 text-primary" />
                      <div>
                        <p className="font-medium">{doc.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {new Date(doc.uploadDate).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {(doc.size / 1024).toFixed(1)} KB
                    </span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
