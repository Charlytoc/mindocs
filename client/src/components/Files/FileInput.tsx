type FileInputProps = {
  label: string;
  accept: string;
  multiple?: boolean;
  onChange: (files: FileList | null) => void;
  name: string;
  required?: boolean;
};

export const FileInput: React.FC<FileInputProps> = ({
  label,
  accept,
  multiple = false,
  onChange,
  name,
  required = false,
}) => (
  <div className="mb-4 flex flex-row gap-2 items-center">
    <label className="block text-xs text-gray-700">{label}</label>
    <input
      required={required}
      name={name}
      type="file"
      accept={accept}
      multiple={multiple}
      onChange={(e) => onChange(e.target.files)}
      className="mt-1 block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer"
    />
  </div>
);
