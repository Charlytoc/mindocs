import { AssetCard } from "./AssetCard";

type Asset = {
  id: string;
  name: string;
  description?: string;
  content: string;
  extracted_text?: string;
  type?: string;
  origin?: "uploaded" | "generated";
  _group?: string;
};

interface AssetListProps {
  assets: Asset[];
  emptyMessage?: string;
  refetchAssets: () => void;
}

export const AssetList = ({
  assets,
  emptyMessage = "No hay documentos asociados aún.",
  refetchAssets,
}: AssetListProps) => {
  if (assets.length === 0) {
    return (
      <div className="col-span-2">
        <div className="text-center py-12">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-gray-100 to-gray-200 mb-4">
            <svg
              className="w-8 h-8 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Sin documentos
          </h3>
          <p className="text-gray-500 max-w-md mx-auto">{emptyMessage}</p>
        </div>
      </div>
    );
  }

  return (
    <>
      {assets.map((asset) => (
        <AssetCard key={asset.id} asset={asset} refetchAssets={refetchAssets} />
      ))}
    </>
  );
};
