import SimpleCrud from '../components/SimpleCrud'
export default function Designations() {
  return <SimpleCrud title="Designations" endpoint="/org/designations"
    fields={[
      { name: 'name', label: 'Name', required: true },
      { name: 'level', label: 'Level', type: 'number', required: true },
    ]}
    columns={[
      { name: 'name', label: 'Name' },
      { name: 'level', label: 'Level' },
    ]} />
}