import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { FileText, Upload, Shield, Zap } from 'lucide-react';

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/30">
      <nav className="border-b">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">Medical Assistant</span>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" asChild>
              <Link to="/login">Login</Link>
            </Button>
            <Button asChild>
              <Link to="/signup">Get Started</Link>
            </Button>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-4 py-20">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h1 className="text-5xl font-bold mb-6">
            Analyze Documents with <span className="text-primary">AI Power</span>
          </h1>
          <p className="text-xl text-muted-foreground mb-8">
            Upload, extract, and manage information from your documents effortlessly. 
            Built for professionals who value simplicity and efficiency.
          </p>
          <div className="flex gap-4 justify-center">
            <Button size="lg" asChild>
              <Link to="/signup">Start Free Trial</Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link to="/login">Sign In</Link>
            </Button>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <div className="text-center p-6">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-lg bg-primary/10 text-primary mb-4">
              <Upload className="h-6 w-6" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Easy Upload</h3>
            <p className="text-muted-foreground">
              Drag and drop your documents or click to upload. Supports images and PDFs.
            </p>
          </div>

          <div className="text-center p-6">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-lg bg-primary/10 text-primary mb-4">
              <Zap className="h-6 w-6" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Fast Processing</h3>
            <p className="text-muted-foreground">
              Extract information from your documents in seconds with powerful analysis.
            </p>
          </div>

          <div className="text-center p-6">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-lg bg-primary/10 text-primary mb-4">
              <Shield className="h-6 w-6" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Secure Storage</h3>
            <p className="text-muted-foreground">
              Your documents are stored securely and accessible only to you.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Index;
