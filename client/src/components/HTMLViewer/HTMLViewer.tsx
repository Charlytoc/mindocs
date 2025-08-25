export const HTMLViewer = ({ html }: { html: string }) => {
  // This component must show SAFE html, maybe using an iframe
  return (
    <iframe
      srcDoc={html}
      className="w-full h-full"
      sandbox="allow-scripts allow-same-origin"
    />
  );
};